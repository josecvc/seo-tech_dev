const form = document.getElementById("form")
const cID = document.getElementById("collection_id")


addEventListener("DOMContentLoaded", (event) => {
    document.getElementById("game_id").value = "0"
    gameTitle.value = ""
});

form.addEventListener("submit", (event) => {
    event.preventDefault()
    if (document.getElementById("game_id").value == "0") {
        alert("Add a game before continuing.")
    } else {
        fetch("/addtocollection", { // send the event id and the requested email
        method: "POST",
        body: JSON.stringify({
            collection_id: cID.value,
            game_id: document.getElementById("game_id").value
        }),
        headers: {
            "Content-type" : "application/json; charset=UTF-8"
        }
    }).then(() => location.reload())
    }
})


