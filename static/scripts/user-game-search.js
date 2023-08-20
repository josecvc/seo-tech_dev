const search = document.getElementById("searchbox")
const suggResults = document.getElementById("suggest-results")
const placeholder = document.getElementById("suggest-placeholder")
const gameTitle = document.getElementById("game_title")

search.addEventListener("submit", (event) => {
    event.preventDefault()
    fetch(`/suggestgames?q=${gameTitle.value}`, { // send the title query
    method: "GET",
    headers: {
        "Content-type" : "application/json; charset=UTF-8"
        }
    })
    .then((response) => response.json())
    .then((json) => buildSuggetions(json))
})

function buildSuggetions(results) {
    /*
    <div id="game-{{game-id}}" class="game-card">
        <span>{{game.title}}<span>
    </div>
    */
    placeholder.remove() // Once suggestions are in, remove them
    suggResults.innerHTML = "";

    if(results.length == 0) {
        suggResults.innerHTML = '<span id="suggest-placeholder">No results...</span>';
    } else {
        for(let id in results) {
            game = results[id]
            newCard = document.createElement("div")
            newCard.id = game["id"]
            newCard.classList.add("game-card")

            newCard.innerHTML = `<div class="log-info"><p>${game["title"]}</p></div>`

            imageBackdrop = document.createElement("div")
            imageBackdrop.classList.add("image-backdrop")
            imageBackdrop.innerHTML = `<img class="backdrop-pic" src="${game["background"]}">
            <div class="part-blur">
            </div>`
            newCard.appendChild(imageBackdrop)
            suggResults.appendChild(newCard)
        }
        document.querySelectorAll(".game-card").forEach(elem => elem.addEventListener("click", () => {
            elem.style.borderRadius = "10px"
            document.getElementById("game_id").value = elem.id
            document.getElementById("show-chosen").innerHTML = "Selected"
            document.getElementById("suggest-focus").innerHTML = elem.outerHTML
        }))
    }
}