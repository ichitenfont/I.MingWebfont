# I.明體 網頁字型

## 原字型說明

[「I.明體（I.Ming）」](https://github.com/ichitenfont/I.Ming) 乃係一套依照傳承字形標準化文件《傳承字形部件檢校表》的推薦字形標準，並以TrueType格式封裝、依照Unicode編碼的OpenType字型。

我們希望「I.明體」可以作爲實際示範，讓大家明白製作字型時，可以採用依照傳承字形標準化文件推薦字形，同時仍然依照Unicode編碼、符合OpenType技術，並期待各字型廠商、字型製作者都能仿效，推出更多開源或商業市場上的傳承字形字型，以收拋磚引玉之效。

「I.明體」這字型名稱裏的「I」是羅馬數字「一」，「I.」唸作「一點（[粵]Jat1 dim2、[中古]Qit temq、[客]Jit7 diam3、[北]Yī diǎn、[日]いちてん、[英]One-dot）」，象徵筆畫的基本：點與線。

使用「I.明體」時，請遵從「[IPA開放字型授權協議 1.0版](https://github.com/ichitenfont/I.Ming/blob/master/LICENSE_CHI.md)（[IPA Open Font License v1.0](https://github.com/ichitenfont/I.Ming/blob/master/LICENSE.md#ipa-font-license-agreement-v10)，[IPAフォントライセンスv1.0](https://github.com/ichitenfont/I.Ming/blob/master/LICENSE.md)）」之規定。

但凡有任何人使用、複製、修改、分發本字型，或對本字型進行任何符合「IPA開放字型授權協議 1.0版」規定的行爲，使用、下載或行使合約規定權利之接受方，亦視爲同意遵守「IPA開放字型授權協議 1.0版」的一切規定。

「IPA字型（IPA Font，IPAフォント）」爲日本「獨立行政法人情報処理推進機構」（簡稱「IPA」）的註冊商標。

## 使用方式

本倉庫用提供「I.明體」自動子集化的網頁字型（webfont）。若需要使用「I.明體」系列網頁字型，可透過 [jsDelivr](https://jsdelivr.net) 如下引用 CSS 文件。

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/ichitenfont/I.MingWebfont/index.css">
```

然後在 CSS 中引用字型的英文名稱：

```css
body {
    font-family: "I.Ming", "I.MingCP", "I.MingVar", "I.MingVarCP", serif;
}
```

若只需要使用「I.明體」系列的某個字型，可修改上面的 `href` 網址爲下列網站：

* 「一點明體」（I.Ming）：`https://cdn.jsdelivr.net/gh/ichitenfont/I.MingWebfont/I.Ming/I.Ming.css`
* 「一點明體CP」（I.MingCP）：`https://cdn.jsdelivr.net/gh/ichitenfont/I.MingWebfont/I.MingCP/I.MingCP.css`
* 「一點明體異體」（I.MingVar）：`https://cdn.jsdelivr.net/gh/ichitenfont/I.MingWebfont/I.MingVar/I.MingVar.css`
* 「一點明體異體CP」（I.MingVarCP）：`https://cdn.jsdelivr.net/gh/ichitenfont/I.MingWebfont/I.MingVarCP/I.MingVarCP.css`

本倉庫不提供「新一細明體」的網頁字型（該字型僅作爲度量相容字型而修改，無必要使用於網頁），使用者應使用原本的「一點明體CP」。

## 授權

本倉庫的代碼以「[共享創意-署名4.0授權協議](https://creativecommons.org/licenses/by/4.0/)（CC BY 4.0）」授權。

本倉庫使用的「I.明體」以「[IPA開放字型授權協議 1.0版](https://github.com/ichitenfont/I.Ming/blob/master/LICENSE_CHI.md)（[IPA Open Font License v1.0](https://github.com/ichitenfont/I.Ming/blob/master/LICENSE.md#ipa-font-license-agreement-v10)，[IPAフォントライセンスv1.0](https://github.com/ichitenfont/I.Ming/blob/master/LICENSE.md)）」使用分發。