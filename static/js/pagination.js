// Fetches paginated list pages in place, so clicking "next"/"previous"
// doesn't change the URL or trigger a full page navigation.
document.addEventListener("click", function (event) {
  var link = event.target.closest("#paginated-region .pagination a");
  if (!link) return;
  event.preventDefault();

  var region = link.closest("#paginated-region");
  var href = link.getAttribute("href");

  fetch(href, { headers: { "X-Requested-With": "XMLHttpRequest" } })
    .then(function (response) {
      return response.text();
    })
    .then(function (html) {
      var doc = new DOMParser().parseFromString(html, "text/html");
      var newRegion = doc.getElementById("paginated-region");
      if (newRegion) {
        region.innerHTML = newRegion.innerHTML;
        region.scrollIntoView({ block: "start", behavior: "smooth" });
      } else {
        window.location.href = href;
      }
    })
    .catch(function () {
      window.location.href = href;
    });
});
