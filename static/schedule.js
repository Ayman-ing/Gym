function toggleInput() {
    var choice = document.getElementById("choice").value;
    var inputContainer = document.getElementById("inputContainer");
    var inputField = document.getElementById("inputField");

    if (choice === "show") {
        inputContainer.style.display = "block";
        inputField.required = true;
    } else {
        inputContainer.style.display = "none";
        inputField.required = false;
    }
}
