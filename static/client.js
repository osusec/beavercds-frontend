console.log("hewwo :3");

/* Helper functions for the scoreboard */

function _calculate_points (min_points, max_points, num_solves, threshold)
{
    // max + (min-max)*solves^2/threshold^2
    let temp = (num_solves**2)/(threshold**2);
    temp *= (min_points - max_points);
    temp += max_points;
    temp = Math.floor(temp);
    return Math.max(temp, min_points);
}

function _calculate_team_points (chals_solved, chals_lookup, time_of_solve)
{
    let total = 0;
    chals_solved.forEach((chal) =>
    {
        total += chals_lookup.get(chal);
    });
    return total;
}

async function scores_over_time ()
{
    // Fetch data. If there's an error hitting the server,
    //  then return an empty array for the Chart.js dataset.
    const response = await fetch ("/allsolves/");
    if (!response.ok) return [];
    data = await response.json();

    // Initialize lookup dictionaries.
    let chals_lookup = new Map();
    let teams_lookup = new Map();

    // Populate chals_lookup.
    data.chals.forEach((chal, index) =>
    {
        let points_info = {
            "min_points": chal.min_points,
            "max_points": chal.max_points,
            "num_solves": 0
        };
        chals_lookup.set(chal.chal_id, points_info)
    });

    // Populate teams_lookup.
    data.teams.forEach((team) =>
    {
        let team_info = {
            "solved_chals": new Array(),
            "points_over_time": new Array()
        };
        team_info.points_over_time.push({
            x: new Date(data.ctf_start_time),
            y: 0
        });
        teams_lookup.set(team.team_name, team_info);
    });

    // Process challenge solves, in chronological order,
    //  and incrementally build graph data.
    // This is not particularly optimized.
    data.solves.forEach((solve, index) =>
    {
        chal_id = solve.challenge__chal_id;
        time_of_solve = solve.time_of_solve;
        team_of_solve = solve.team__team_name;

        solved_chal = chals_lookup.get(chal_id);

        // Register the solve.
        solved_chal.num_solves += 1;
        teams_lookup.get(team_of_solve).solved_chals.push(chal_id);

        // Per new solve, recalculate each challenge's current
        //  value at that point in time.
        let chal_point_in_time = new Map();
        chals_lookup.forEach((chal, chal_id) =>
        {
            const current_value = _calculate_points(
                chal.min_points,
                chal.max_points,
                chal.num_solves,
                data.threshold_solves
            );
            chal_point_in_time.set(chal_id, current_value);
        });

        // Per new solve, recalculate each team's current points
        //  total. Insert this into the final array with the time
        //  of solve.
        // This creates a `teams*time` array.
        teams_lookup.forEach((team, team_id) =>
        {
            const total_points = _calculate_team_points (
                team.solved_chals,
                chal_point_in_time,
                time_of_solve
            );
            team.points_over_time.push({
                x: new Date(time_of_solve),
                y: total_points
            });
        });
    });

    // Format for Charts.js
    dataset = new Array();
    teams_lookup.forEach((team, team_id) => {
        dataset.push({
            label: team_id,
            data: team.points_over_time
        });
    });

    return dataset;
}

/* end Helper functions for the scoreboard */


// Timezone settings
const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
document.cookie = `timezone=${encodeURIComponent(timezone)}`;

// Logout button
document.querySelectorAll("#bcds-logout-btn").forEach(element =>
{
    element.addEventListener("click", (event) => 
    {
        document.getElementById("logoutform").submit();
    });
});

// Copy Email Buttons
document.querySelectorAll(".bcds-copy-btn").forEach(element => 
{
    element.addEventListener("click", (event) => 
    {
        const button = event.target;
        const link_id = event.target.dataset.linkId;
        const link = document.getElementById(link_id).value;
        navigator.clipboard.writeText(link);
        const tooltip = new bootstrap.Tooltip(button, {
            title: 'Copied',
            customClass: 'border-success'
        });
        tooltip.show();
    });
});

// Bracket selector and password fields
document.querySelectorAll("#selectBracketGroup").forEach(element =>
{
    element.addEventListener("change", (event) =>
    {
        const bracketSelect = event.target.querySelector(".bracket-select:checked")
        const bracket_pw_id = bracketSelect.dataset.passwordId;
        var bracket_pw = document.getElementById(bracket_pw_id);

        document.querySelectorAll(".bracket_password").forEach(element =>
        {
            element.hidden = true;
        });
        bracket_pw.hidden = false;
    });
});

// Perform AJAX style error handling on forms
document.querySelectorAll(".bcds-form").forEach(element =>
{
    element.addEventListener("submit", async (event) => 
    {
        event.preventDefault();

        const form = event.target;
        const button = event.submitter;
        const response = await fetch (form.action,
        {
            method: form.method,
            body: new FormData(form)
        });

        const result = await response.json();
        if (response.ok)
        {
            window.location.href = result.redirect;
        }
        else
        {
            const errors = result.errors.join("<br>")
            var popover = new bootstrap.Popover(button, {
                content: errors,
                html: true,
                customClass: "border-danger-subtle",
                placement: "right",
            });
            popover.show();
        }
    });
});

// Initialize and populate the scoreboard
document.querySelectorAll("#bcds-scoreboard").forEach(async (element) =>
{
    dataset = await scores_over_time();
    
    const chart = new Chart(element, {
        type: 'line',
        data: {datasets: dataset},
        options: {
            scales: {
                x: {type: 'time', time: { tooltipFormat: 'DD T' }},
                y: {type: 'linear', beginAtZero: true}
            },
            pointStyle: false
        }
    });

    // Update the scoreboard every 10 minutes
    setInterval(async () =>
    {
        dataset = await scores_over_time();
        if (dataset.length != 0) {
            chart.data.datasets = dataset;
            chart.update('none');
        }

    }, 600000);
});


// Initialize tooltips
const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

// Initialize popovers
const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
popoverList.map(popoverEl => popoverEl.show());
