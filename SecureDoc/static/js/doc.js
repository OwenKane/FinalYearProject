/**
 * Created by owenkane on 02/02/2017.
 */

window.addEventListener("load", function(){
    //first check if execCommand and contentEditable attribute is supported or not.
    if(document.contentEditable != undefined && document.execCommand != undefined)
    {
        alert("HTML5 Document Editing API Is Not Supported");
    }
    else
    {
        document.execCommand('styleWithCSS', false, true);
    }
}, false);

//underlines the selected text
function underline() {
    document.execCommand("underline", false, null);
}

//makes the selected text as hyperlink.
function link() {
    var url = prompt("Enter the URL");
    document.execCommand("createLink", false, url);
}

//displays HTML of the output
function displayhtml() {
    //set textContent of pre tag to the innerHTML of editable div. textContent can take any form of text and display it as it is without browser interpreting it. It also preserves white space and new line characters.
    document.getElementsByClassName("htmloutput")[0].textContent = document.getElementsByClassName("editor")[0].innerHTML;
}
