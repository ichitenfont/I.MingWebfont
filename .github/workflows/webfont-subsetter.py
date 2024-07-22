from fontTools.subset import main as ftSubset
from fontTools.ttLib import TTFont

from pathlib import Path
from multiprocessing import Pool

import json
import os, sys, shutil

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)

# get list of characters
def get_charset(ttfont:TTFont):
    chars = set(y for x in ttfont["cmap"].tables for y in x.cmap.keys())
    return chars

# get list of features
def get_all_features(ttfont:TTFont):
    gpos = [feature.FeatureTag for feature in ttfont['GPOS'].table.FeatureList.FeatureRecord]
    gsub = [feature.FeatureTag for feature in ttfont['GSUB'].table.FeatureList.FeatureRecord]
    return gpos + gsub

def group_char_as_range_tuple(charlist):
    # grouping characters to range
    grouped_list = []
    current_range_start = 0
    current_range_index = 0
    for char in charlist:
        # skip C0
        if char < 0x20:
            continue

        # initialise
        if current_range_index == 0:
            current_range_start = char
            current_range_index = char
            continue

        if char == current_range_index + 1:
            current_range_index = char
        else:
            grouped_list.append((current_range_start, current_range_index))
            current_range_start = char
            current_range_index = char
    return grouped_list

def merge_char_range_to_css_unicode_list(grouped_list):
    MAX_RANGE_SIZE_LIMIT = 0x80
    
    # merge list to CSS Unicode style, eg U+20,U+31-3F
    output_range = []
    seen_index = []
    for index, (start, end) in enumerate(grouped_list):
        if index in seen_index:
            continue
        seen_index.append(index)
        
        current_size = end - start + 1
        current_merged_range = [(start, end)]
        next_index = index + 1
        if current_size < MAX_RANGE_SIZE_LIMIT:
            # try to add until size 0x80
            while current_size < MAX_RANGE_SIZE_LIMIT and next_index < len(grouped_list):
                next_start, next_end = grouped_list[next_index]
                if current_size + next_end - next_start + 1 < MAX_RANGE_SIZE_LIMIT:
                    current_merged_range.append((next_start, next_end))
                    current_size = current_size + next_end - next_start + 1
                    seen_index.append(next_index)
                    next_index += 1
                else:
                    break
            output_range.append(current_merged_range)
        elif current_size > MAX_RANGE_SIZE_LIMIT:
            # too large, insert directly
            # break start up to 0x??7F
            first_end = start + (MAX_RANGE_SIZE_LIMIT - (start % MAX_RANGE_SIZE_LIMIT)) - 1 # 0x7F
            output_range.append([(start, first_end)])
            
            current_value = first_end + 1 # 0x80
            next_value = first_end + MAX_RANGE_SIZE_LIMIT # 0xFF
            while next_value <= end:
                output_range.append([(current_value, next_value)])
                current_value = next_value + 1 # 0x00
                next_value = next_value + MAX_RANGE_SIZE_LIMIT # 0x7F
            
            if next_value != end:
                output_range.append([(current_value, end)])
        else:
            # just add the range
            output_range.append(current_merged_range)
    return output_range

# generates unicode.json file
def generate_unicode_json(ttfont:TTFont, output_filename, override:list|tuple=None):
    '''
    ttfont: TTFont object
    output_filename: output JSON path
    override: list of characters (maintaining order) to subset together first, before processing the remaining chars
    '''
    # get unicode character list in font
    charlist = sorted(list(get_charset(ttfont)))
    # prepare in order
    if override is not None:
        assert type(override) in [list, tuple]
        override = [ord(x) for x in override]
        override = list(dict.fromkeys(override))
        charlist = [x for x in charlist if x not in override]

        to_be_merged_char_range_tuple = [group_char_as_range_tuple(override), group_char_as_range_tuple(charlist)]
    else:
        to_be_merged_char_range_tuple = [group_char_as_range_tuple(charlist)]
    
    output_range = []
    for char_range_tuple in to_be_merged_char_range_tuple:
        output_range += merge_char_range_to_css_unicode_list(char_range_tuple)

    # write unicode.json file
    with open(output_filename, "w") as f:
        f.write("{")

        converted_ranges = []
        for index, ranges in enumerate(output_range):
            # write starting index
            ranges_str = (r'"%d": "' % index)

            converted_hex=[]
            for start, end in ranges:
                range_str = "U+" + hex(start)[2:].upper()
                if start != end: # multiple value
                    range_str += "-" + hex(end)[2:].upper()
                converted_hex.append(range_str)
            
            ranges_str += ",".join(converted_hex)
            ranges_str += '"'
            converted_ranges.append(ranges_str)
        
        f.write(",\n".join(converted_ranges))
        f.write("\n")
        f.write("}")


def prepare_font_subset(source_file, css_font_family_name, output_parent=None, json_path=None, acronym=None, layout_features=None):
    """
    Subset the source file to a series of webfont with the given CSS font-family name. 
    Returns a series of output path and arguments to fontTools subset.
    Will create unicode.json file and the appropriate css files with unicode-range.
    font_weight: numeric value or string for CSS font-weight
    output_parent: root folder for all the woff2 and css file for this source file output
    acronym: shorter name for output file, ignore will use source_file name
    """
    filename, extension = os.path.splitext(os.path.basename(source_file))
    # set default values
    if acronym is None:
        acronym = filename
    if output_parent is None:
        output_parent = os.path.join(os.path.split(source_file)[0], "out")
    if json_path is None:
        json_path = os.path.join(os.path.split(source_file)[0], "unicode.json")
    if layout_features is None:
        layout_features = get_all_features(TTFont(source_file, 0, allowVID=0,
                    ignoreDecompileErrors=True,
                    fontNumber=-1))
    ensure_dir(output_parent)

    # read subsetting json
    with open(json_path, 'r') as f:
        # generate css files
        tasks = []
        css = ""
        for subset_id, unicode in json.load(f).items():
            out_file = acronym + "-sub{}.woff2".format(subset_id)
            out_path = os.path.join(output_parent, out_file)
            # subset css
            css_part = (
                "/* {} [{}] */\n".format(acronym, subset_id),
                "@font-face {\n",
                "  font-family: '{}';\n".format(css_font_family_name),
                "  font-style: normal;\n",
                "  font-display: block;\n",
                "  src: url('./{}') format('woff2');\n".format(out_file),
                "  unicode-range: {}\n".format(unicode),
                "}\n"
            )
            css += "".join(css_part)
            # subset font arguments
            args = [
                source_file,
                "--output-file={}".format(out_path),
                "--flavor=woff2",
                "--unicodes={}".format(unicode),
                "--layout-features=" + ",".join(layout_features),
                "--passthrough-tables",
            ]
            tasks.append((out_path, args))
    
    # save css file with family name to avoid include version number
    css_filename = css_font_family_name + ".css"
    css_path = os.path.join(output_parent, css_filename)
    with open(css_path, 'w', newline='\n') as f:
        f.write(css)
    
    # return tasks of subsetting
    return (tasks, css_filename)


# run subsetting on the output of prepare_font_subset()
def subset_worker(task):
    out_file, args = task
    print("Generating {}".format(out_file))
    ftSubset(args)

def is_number(s):
    try:
        float(s) # for int, long, float
    except ValueError:
        return False
    return True

def detect_latest_version(iming_src_repo):
    dir_content = os.listdir(iming_src_repo)
    dir_list =[entry for entry in dir_content if os.path.isdir(os.path.join(iming_src_repo, entry)) and is_number(entry)]
    sorted_list = sorted(dir_list, reverse=True, key=float)
    return sorted_list[0]

def subset_iming():    
    subset_font_prefix = ["I.Ming", "I.MingCP", "I.MingVar", "I.MingVarCP"]
    acronyms = ["im", "imcp", "imv", "imvcp"]
    unicode_json_path = "unicode.json"
    version_filename = "VERSION"
    
    # 檢查最新的版本
    iming_src_repo = "iming-src"
    latest_ver = detect_latest_version(iming_src_repo)
    # note down version
    with open(version_filename, 'w') as f:
        f.write(latest_ver)

    # 检查存在的字体
    fonts_to_subset = []
    for index, webfont_root_dir in enumerate(subset_font_prefix):
        font_relative_path = os.path.join(iming_src_repo, latest_ver, webfont_root_dir + "-" + latest_ver + ".ttf")
        if os.path.isfile(font_relative_path):
            fonts_to_subset.append({
                "family-name": webfont_root_dir,
                "path": font_relative_path, 
                "acronym": acronyms[index],
                "root": webfont_root_dir,
            })
            
            # 删除存在的之前的webfont
            if os.path.exists(webfont_root_dir):
                shutil.rmtree(webfont_root_dir)
    
    # 读取需要优先的字符列表
    priority_filename = "priority_char_list.txt"
    if os.path.exists(priority_filename):
        priority_list = [line.strip() for line in open(priority_filename, "r", encoding="utf-8")]
    else:
        priority_list = []

    # 打开字体，生成 Unicode 字表和 opentype 功能
    ttf = TTFont(fonts_to_subset[0]["path"], 0, allowVID=0,
                    ignoreDecompileErrors=True,
                    fontNumber=-1)
    generate_unicode_json(ttf, unicode_json_path, override=priority_list)
    layout_features = get_all_features(ttf)

    tasks = []
    main_css = ""
    for fontobj in fonts_to_subset:
        # create folder for font
        webfont_root = fontobj["root"]
        ensure_dir(webfont_root)
        # make css file and tasks
        subtask, css_filename = prepare_font_subset(fontobj["path"], fontobj["family-name"], webfont_root, unicode_json_path, acronym=fontobj["acronym"], layout_features=layout_features)

        tasks += subtask
        main_css += "@import url('./%s');\n" % os.path.join(webfont_root, css_filename).replace("\\", "/")
    
    # save main css file
    main_css_path = "index.css"
    with open(main_css_path, 'w', newline='\n') as f:
        f.write(main_css)

    # subset fonts in parallel
    with Pool(8) as pool:
        pool.map(subset_worker, tasks)

if __name__ == '__main__':
    subset_iming()