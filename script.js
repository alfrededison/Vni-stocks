document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("table tr").forEach(row => {
        let lastCell = row.querySelector("td:last-child");
        let secondLastCell = row.querySelector("td:nth-last-child(2)");
        let sixthCell = row.querySelector("td:nth-child(6)");

        if (lastCell && lastCell.textContent.trim() === "1") {
            lastCell.style.backgroundColor = "red";
            if (sixthCell) {
                sixthCell.style.backgroundColor = "red";
            }
        }
        if (secondLastCell && secondLastCell.textContent.trim() === "1") {
            secondLastCell.style.backgroundColor = "green";
            if (sixthCell) {
                sixthCell.style.backgroundColor = "green";
            }
        }
    });
});