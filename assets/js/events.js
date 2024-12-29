function setup_info_on_click(){
	function toggle_info(e){
		let event = e.target.closest(".event");
		let info = event.querySelector(".info");
		info.classList.toggle("active");
	}

	let flyers = document.querySelectorAll(".flyer");
	flyers.forEach((flyer, index) => {
		// on click, show/hide the info div
		flyer.addEventListener("click", toggle_info);
	});
}
setup_info_on_click();

function hide_past_events(){
	let cal = document.querySelector("#calendar");

	window.old_events = [];

	let show_old_button = document.querySelector("#show-old-events");
	show_old_button.addEventListener("click", (e) => {
		window.old_events.forEach((event) => {
			cal.appendChild(event);
		});
		window.old_events = [];
	});
	// get all the events
	let events = document.querySelectorAll(".event");

	let d = new Date();

	// today as 'yyyymmdd'
	let formatted_date =
		String(d.getFullYear()) +
		String(d.getMonth() + 1).padStart(2, '0') +
		String(d.getDate()).padStart(2, '0')

	let today = parseInt(formatted_date);


	// delete past events
	events.forEach((event) => {
		let event_date = parseInt(event.dataset.date);
		console.log(event_date, today);
		if(today > event_date){
			window.old_events.push(cal.removeChild(event));
		}
	});
}

hide_past_events();
