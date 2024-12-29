window.current_bg_img = 0
function rotate_backgrounds(){
	let mask = document.querySelector("#header-img-mask");
	let header = document.querySelector("header");

	mask.classList.toggle("black-background");

	// wait 2s for the background to darken
	setTimeout(function(){
		// change the photo
		current_bg_img++;
		current_bg_img = current_bg_img >= header.dataset.numImages ? 0 : current_bg_img;
		let next_url = document.querySelector("#site-url").innerText + "/assets/images/homepage_photos/photo_"+ current_bg_img +".jpg";

		header.style.backgroundImage = "url('"+next_url+"')";

		mask.classList.toggle("black-background")
	}, 2000)

}

setInterval(rotate_backgrounds, 5000)

