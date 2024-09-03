const body = document.querySelector('body');
const pane = document.getElementById('navbar-pane');
const toggle = document.getElementById('navbar-toggle');
const overlay = document.getElementById('navbar-overlay');

if (body && pane && toggle && overlay) {
    [toggle, overlay].forEach((el) => {
        el.addEventListener('click', () => {
            body.classList.toggle('show-pane');
        });
    });
}

for (const section of document.querySelectorAll('#navbar-full section')) {
    const dropdown = section.querySelector('.dropdown');
    const toggle = section.querySelector('.dropdown-toggle');

    if (!dropdown || !toggle)
        continue;

    section.addEventListener('mouseover', () => {
        section.classList.add('show-dropdown');
    });
    section.addEventListener('mouseout', () => {
        section.classList.remove('show-dropdown');
    });
    toggle.addEventListener('click', (e) => {
        e.preventDefault();
        section.classList.toggle('show-dropdown');
    });
}
