var doc = app.activeDocument;
var fonts = {};

for (var i = 0; i < doc.textFrames.length; i++) {
    var textFrame = doc.textFrames[i];
    for (var j = 0; j < textFrame.characters.length; j++) {
        var character = textFrame.characters[j];  // Changed from 'char' to 'character'
        var fontName = character.characterAttributes.textFont.name;
        fonts[fontName] = true;
    }
}

var fontList = "Fonts used in document:\n\n";
for (var font in fonts) {
    fontList += font + "\n";
}

alert(fontList);