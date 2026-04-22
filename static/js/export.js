function exportDashboard() {

    const dashboard = document.querySelector(".container");

    html2canvas(dashboard).then(canvas => {

        const link = document.createElement("a");

        link.download = "dashboard.png";

        link.href = canvas.toDataURL();

        link.click();

    });

}