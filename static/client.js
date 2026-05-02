console.log("hewwo :3");

// Timezone settings
const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
document.cookie = `timezone=${encodeURIComponent(timezone)}`;

// Logout button
document.getElementById("bcds-logout-btn")
.addEventListener("click", (event) => 
{
    document.getElementById("logoutform").submit();
});

// Copy Email Buttons
Array.from(document.getElementsByClassName("bcds-copy-btn")).forEach(element => 
{
    element.addEventListener("click", (event) => 
    {
        const button = event.target;
        const link_id = event.target.dataset.linkId;
        const link = document.getElementById(link_id).value;
        navigator.clipboard.writeText(link);
    });
});
