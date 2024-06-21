const showSidebar=()=>{
    console.log("clicked")
    const sidebar=document.querySelector(".sidebar")
    sidebar.style.display="flex"
    const navbar=document.querySelector(".navbar")
    navbar.style.display="none"

}
const hideSidebar=()=>{
    console.log("clicked hide")
    const sidebar=document.querySelector(".sidebar")
    sidebar.style.display="none"
    const navbar=document.querySelector(".navbar")
    navbar.style.display="flex"
}
const menu=document.getElementById("menu");
menu.addEventListener("click",showSidebar);

const cross=document.getElementById("cross");
cross.addEventListener("click",hideSidebar);