const modalButton = document.getElementById("create-popup")

modalButton.addEventListener("click", (event) =>{
    event.preventDefault()
    modal.style.display = "block" // show the collection form tab
}
)

window.addEventListener("click", (event) => {
    if(event.target == modal) { modal.style.display = "none" }
}
)