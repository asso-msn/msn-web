function cleanUrlParams() {
    const url = new URL(location.href);
    for (const key of url.searchParams.keys()) {
        if (url.searchParams.get(key) === "")
            url.searchParams.delete(key);
    }
    history.replaceState({}, "", url);
}

for (const el of document.querySelectorAll(".input .password")) {
    const show = el.querySelector(".show");
    const hide = el.querySelector(".hide");
    const input = el.querySelector("input");

    if (!show || !hide || !input)
        continue;

    el.classList.add("hide");

    show.addEventListener("click", () => {
        el.classList.remove("hide");
        el.classList.add("show");
        input.type = "text";
    });
    hide.addEventListener("click", () => {
        el.classList.remove("show");
        el.classList.add("hide");
        input.type = "password";
    });
}

for (const el of document.querySelectorAll("select option")) {
    if (el.value === "" && el.text.trim().replace(/-/g, "").length === 0)
        el.disabled = true;
}
