const allStar = document.querySelectorAll('.rating .star')
const ratingValue = document.getElementById("rating-value")
const ratingForm = document.getElementById("rating-form")

allStar.forEach((item, idx)=> {
	item.addEventListener('click', function () {
		let click = 0
		ratingValue.value = idx + 1

		allStar.forEach(i=> {
			i.classList.replace('bxs-star', 'bx-star')
			i.classList.remove('active')
		})
		for(let i=0; i<allStar.length; i++) {
			if(i <= idx) {
				allStar[i].classList.replace('bx-star', 'bxs-star')
				allStar[i].classList.add('active')
			} else {
				allStar[i].style.setProperty('--i', click)
				click++
			}
		}
	})
})

ratingForm.addEventListener("submit", (event) => {
    event.preventDefault()
    if(ratingValue.value >= 1 && ratingValue.value <=5) {
        let reviewText = null
        if(document.getElementById("review") != "") { // If there is a review
            reviewText = document.getElementById("review").value
        }
        console.log("HEY")
        fetch("/addrating", {
            method:"POST",
            body: JSON.stringify( {
                game_id: document.getElementById("hidden_game_id").value,
                rating: ratingValue.value,
                review: reviewText
            }),
            headers: {
                "Content-type" : "application/json; charset=UTF-8"
            }
        })
        .then(() => location.reload())
    } else {
        event.preventDefault()
    }
})
