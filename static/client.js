console.log("hewwo :3");

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

/* under TODO */
function calculate_points (min_points, max_points, num_solves, threshold)
{
    // max + (min-max)*solves^2/threshold^2
    let temp = (num_solves**2)/(threshold**2);
    temp *= (min_points - max_points);
    temp += max_points;
    temp = Math.floor(temp);
    return Math.max(temp, min_points);
}

function calculate_team_points (chals_solved, chals_lookup, time_of_solve)
{
    let total = 0;
    chals_solved.forEach((chal) =>
    {
        total += chals_lookup.get(chal);
    });
    return total;
}

async function get_data ()
{
    const response = await fetch ("/allsolves/");
    if (response.ok)
    {
        return response.json();
    }
    return {};
}

function scores_over_time (data)
{
    let chals_lookup = new Map();
    let teams_lookup = new Map();

    data.chals.forEach((chal, index) =>
    {
        let points_info = {
            "min_points": chal.min_points,
            "max_points": chal.max_points,
            "num_solves": 0
        };
        chals_lookup.set(chal.chal_id, points_info)
    });

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

    data.solves.forEach((solve, index) =>
    {
        chal_id = solve.challenge__chal_id;
        time_of_solve = solve.time_of_solve;
        solved_chal = chals_lookup.get(chal_id);
        solved_chal.num_solves += 1;

        let chal_point_in_time = new Map();
        chals_lookup.forEach((chal, chal_id) =>
        {
            const current_value = calculate_points(
                chal.min_points,
                chal.max_points,
                chal.num_solves,
                data.threshold_solves
            );
            chal_point_in_time.set(chal_id, current_value);
        });

        team_of_solve = solve.team__team_name;
        teams_lookup.get(team_of_solve).solved_chals.push(chal_id);

        teams_lookup.forEach((team, team_id) =>
        {
            team_point_in_time = team.solved_chals;
            const total_points = calculate_team_points (team_point_in_time, chal_point_in_time, time_of_solve);
            team.points_over_time.push({
                x: new Date(time_of_solve),
                y: total_points
            });
        });
    });

    return teams_lookup;
}

// Scoreboard
document.querySelectorAll("#bcds-scoreboard").forEach(async (element) =>
{
    data = await get_data();
    teams_lookup = scores_over_time(data);

    dataset = new Array();
    teams_lookup.forEach((team, team_id) => {
        dataset.push({
            label: team_id,
            data: team.points_over_time
        });
    });

    const ctx = element;
    new Chart(ctx, {
        type: 'line',
        data: {
            datasets: dataset
        },
        options: {
            scales: {
                x: {
                    type: 'time',
                    time: { tooltipFormat: 'DD T' }
                },
                y: {
                    type: 'linear',
                    beginAtZero: true,
                }
            },
            pointStyle: false
        }
    });
});
/* end TODO */

// Initialize tooltips
const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

// Initialize popovers
const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
popoverList.map(popoverEl => popoverEl.show());
