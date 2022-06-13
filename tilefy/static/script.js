
// set background color for preview boxes
function colorPreview() {
    const allPreviews = document.getElementsByClassName("color-preview");
    for (let i = 0; i < allPreviews.length; i++) {
        const previewElement = allPreviews[i];
        const backgroundColor = previewElement.getAttribute("data-id")
        previewElement.style.backgroundColor = backgroundColor
    }
}

colorPreview();
