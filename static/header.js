// get the :root part in CSS
const root = document.documentElement

const updateDash = function () {
  // how far down the page have we scrolled?
  const scroll = window.pageYOffset

  // how big should be dash be? 4% of the scroll distance
  const size = 16 + scroll * 0.04

  // capped it so it doesn't get too big or small
  const cappedSize = Math.max(16, Math.min(size, 64))

  // update CSS accordingly
  root.style.setProperty("--dash-size", `${cappedSize}px`)
}

// run the above function on load
updateDash()

// ...and on any scroll event
window.addEventListener("scroll", function () {
  updateDash()
})