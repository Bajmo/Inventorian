function openNav() {
    document.getElementById("sideBar").style.width = "250px";
    document.getElementById("toggle_dropdown").classList.remove("dropdown-toggle");
}

function closeNav() {
    document.getElementById("sideBar").style.width = "0";
    document.getElementById("toggle_dropdown").classList.add("dropdown-toggle");
}
