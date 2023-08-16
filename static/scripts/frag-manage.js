const form = document.getElementById("form")

form.addEventListener("submit", (event) => {
    event.preventDefault()
    if (document.getElementById("game_id").value == "0") {
        alert("Add a game before continuing.")
    } else {
        fetch("/addfrag", { // send the event id and the requested email
        method: "POST",
        body: JSON.stringify({
            game_id: document.getElementById("game_id").value,
            datestamp: document.getElementById("date_started").value,
            timestamp: document.getElementById("time_started").value,
            time_played: document.getElementById("time_played").value,
            unit: document.getElementById("unit").value
        }),
        headers: {
            "Content-type" : "application/json; charset=UTF-8"
        }
    }).then(() => location.reload())
    }
})


