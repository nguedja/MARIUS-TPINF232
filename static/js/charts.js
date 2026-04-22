
// =====================
// FILIÈRES
// =====================
new Chart(document.getElementById('filiereChart'), {
    type: 'pie',
    data: {
        labels: filiereLabels,
        datasets: [{
            data: filiereValues,
            backgroundColor: ['#007bff','#28a745','#ffc107','#dc3545','#6f42c1','#20c997']
        }]
    }
});


// =====================
// ENSEIGNANTS
// =====================
new Chart(document.getElementById('teacherChart'), {
    type: 'bar',
    data: {
        labels: teacherLabels,
        datasets: [{
            data: teacherValues,
            backgroundColor: '#28a745'
        }]
    }
});


// =====================
// SCATTER (NUAGE DE POINTS)
// =====================
new Chart(document.getElementById('scatterChart'), {
    type: 'scatter',
    data: {
        datasets: [{
            label: "Nuage de points",
            data: scatterX.map((x, i) => ({
                x: x,
                y: scatterY[i]
            })),
            backgroundColor: "blue"
        }]
    },
    options: {
        scales: {
            x: { title: { display: true, text: "Satisfaction" } },
            y: { title: { display: true, text: "Étudiants" } }
        }
    }
});

// =====================
// RÉGRESSION LINÉAIRE
// =====================

new Chart(document.getElementById('regressionChart'), {

    type: 'line',

    data: {

        datasets: [

            {
                label: "Droite de régression",

                data: scatterX.map((x, i) => ({
                    x: x,
                    y: regressionLine[i]
                })),

                borderColor: "red",
                borderWidth: 3,
                fill: false,
                pointRadius: 0
            }

        ]
    },

    options: {

        scales: {

            x: {
                type: 'linear',
                title: {
                    display: true,
                    text: "Satisfaction"
                }
            },

            y: {
                title: {
                    display: true,
                    text: "Index étudiant"
                }
            }

        }

    }

});
