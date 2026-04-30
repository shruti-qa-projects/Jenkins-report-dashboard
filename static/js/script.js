function getBranchParam(){
    let branch = document.getElementById("branch").value;
    return branch ? "?branch=" + encodeURIComponent(branch) : "";
}

function generateView(){
    document.getElementById("loader").style.display="block";
    setTimeout(() => {
        window.location.href = "/generate" + getBranchParam();
    }, 500);
}

function generateDownload(){
    document.getElementById("loader").style.display="block";
    setTimeout(() => {
        window.location.href = "/download" + getBranchParam();
    }, 500);
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("branch")?.addEventListener("input", () =>
        document.querySelector(".error-text")?.remove()
    );
});
