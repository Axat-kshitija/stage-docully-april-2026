
/*
Docxgen.coffee
Created by Edgar HIPP
 */
var DocUtils, DocXTemplater, DocxGen, JSZip;

DocUtils = require('./docUtils');

DocXTemplater = require('./docxTemplater');

JSZip = require('jszip');

DocxGen = DocxGen = (function() {
  var templatedFiles;

  templatedFiles = ["word/document.xml", "word/footer1.xml", "word/footer2.xml", "word/footer3.xml", "word/header1.xml", "word/header2.xml", "word/header3.xml"];

  function DocxGen(content, options) {
    this.setOptions({});
    if (content != null) {
      this.load(content, options);
    }
  }

  DocxGen.prototype.setOptions = function(options) {
    this.options = options != null ? options : {};
    this.intelligentTagging = this.options.intelligentTagging != null ? this.options.intelligentTagging : true;
    if (this.options.parser != null) {
      this.parser = options.parser;
    }
    return this;
  };

  DocxGen.prototype.load = function(content, options) {
    if (content.file != null) {
      this.zip = content;
    } else {
      this.zip = new JSZip(content, options);
    }
    return this;
  };

  DocxGen.prototype.render = function() {
    var currentFile, fileName, _i, _len;
    for (_i = 0, _len = templatedFiles.length; _i < _len; _i++) {
      fileName = templatedFiles[_i];
      if (!(this.zip.files[fileName] != null)) {
        continue;
      }
      currentFile = new DocXTemplater(this.zip.files[fileName].asText(), {
        DocxGen: this,
        Tags: this.Tags,
        intelligentTagging: this.intelligentTagging,
        parser: this.parser,
        fileName: fileName
      });
      this.zip.file(fileName, currentFile.render().content);
    }
    return this;
  };

  DocxGen.prototype.getTags = function() {
    var currentFile, fileName, usedTags, usedTemplateV, _i, _len;
    usedTags = [];
    for (_i = 0, _len = templatedFiles.length; _i < _len; _i++) {
      fileName = templatedFiles[_i];
      if (!(this.zip.files[fileName] != null)) {
        continue;
      }
      currentFile = new DocXTemplater(this.zip.files[fileName].asText(), {
        DocxGen: this,
        Tags: this.Tags,
        intelligentTagging: this.intelligentTagging,
        parser: this.parser
      });
      usedTemplateV = currentFile.render().usedTags;
      if (DocUtils.sizeOfObject(usedTemplateV)) {
        usedTags.push({
          fileName: fileName,
          vars: usedTemplateV
        });
      }
    }
    return usedTags;
  };

  DocxGen.prototype.setData = function(Tags) {
    this.Tags = Tags;
    return this;
  };

  DocxGen.prototype.getZip = function() {
    return this.zip;
  };

  DocxGen.prototype.getFullText = function(path) {
    var usedData;
    if (path == null) {
      path = "word/document.xml";
    }
    usedData = this.zip.files[path].asText();
    return (new DocXTemplater(usedData, {
      DocxGen: this,
      Tags: this.Tags,
      intelligentTagging: this.intelligentTagging
    })).getFullText();
  };

  return DocxGen;

})();

DocxGen.DocUtils = DocUtils;

module.exports = DocxGen;
