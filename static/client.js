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

// Initialize tooltips
const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

// Initialize popovers
const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
popoverList.map(popoverEl => popoverEl.show());
