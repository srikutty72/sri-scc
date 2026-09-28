document.addEventListener("DOMContentLoaded", () => {
    console.log("ComicCraft JS loaded");

    const form =
        document.querySelector("form");

    if (!form) {
        console.error("Comic form not found");
        return;
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        console.log("Generate button clicked");

        const button =
            form.querySelector("button[type='submit']");

        if (button) {
            button.disabled = true;
            button.innerText = "Generating...";
        }

        let resultBox =
            document.getElementById("comic-result");

        if (!resultBox) {
            resultBox =
                document.createElement("section");

            resultBox.id = "comic-result";

            resultBox.style.maxWidth = "1100px";
            resultBox.style.margin = "40px auto";
            resultBox.style.padding = "20px";

            form.parentElement.appendChild(resultBox);
        }

        resultBox.innerHTML = `
            <div class="card">
                <h2>Creating your comic...</h2>
                <p>Please wait.</p>
            </div>
        `;

        try {

            const formData =
                new FormData(form);

            const response =
                await fetch("/generate", {
                    method: "POST",
                    body: formData
                });

            const data =
                await response.json();

            console.log("Backend response:", data);

            if (!response.ok) {
                throw new Error(
                    data.detail ||
                    data.error ||
                    "Comic generation failed."
                );
            }

            if (!data.success) {
                throw new Error(
                    data.error ||
                    "Comic generation failed."
                );
            }

            renderComic(data.comic);

        } catch (error) {

            console.error(error);

            resultBox.innerHTML = `
                <div class="card">
                    <h2>Generation Error</h2>
                    <p>${escapeHtml(error.message)}</p>
                </div>
            `;

        } finally {

            if (button) {
                button.disabled = false;
                button.innerText = "Generate Comic";
            }
        }
    });


    function renderComic(comic) {

        const resultBox =
            document.getElementById("comic-result");

        if (!resultBox) return;

        let html = `
            <div class="card">
                <h1>${escapeHtml(
                    comic.title || "My Comic"
                )}</h1>

                <p>
                    ${escapeHtml(
                        comic.logline || ""
                    )}
                </p>

                <hr>

                <h3>Character</h3>

                <p>
                    ${escapeHtml(
                        comic.character || ""
                    )}
                </p>

                <h3>Setting</h3>

                <p>
                    ${escapeHtml(
                        comic.setting || ""
                    )}
                </p>
            </div>

            <div style="
                display:grid;
                grid-template-columns:
                    repeat(auto-fit,minmax(280px,1fr));
                gap:20px;
                margin-top:25px;
            ">
        `;

        const panels =
            comic.panels || [];

        panels.forEach((panel) => {

            html += `
                <div class="card"
                     style="
                        overflow:hidden;
                        padding:0;
                     ">

                    ${
                        panel.image_url
                        ?
                        `
                        <img
                            src="${panel.image_url}"
                            alt="Comic Panel"
                            style="
                                width:100%;
                                display:block;
                            "
                        >
                        `
                        :
                        `
                        <div style="
                            min-height:250px;
                            display:flex;
                            align-items:center;
                            justify-content:center;
                            background:#eeeeee;
                            padding:20px;
                            text-align:center;
                        ">
                            Image not generated
                        </div>
                        `
                    }

                    <div style="padding:20px">

                        <h2>
                            Panel
                            ${panel.panel_number}
                            -
                            ${escapeHtml(
                                panel.title || ""
                            )}
                        </h2>

                        <p>
                            <strong>Scene:</strong><br>
                            ${escapeHtml(
                                panel.scene || ""
                            )}
                        </p>

                        <p>
                            <strong>Narration:</strong><br>
                            ${escapeHtml(
                                panel.narration || ""
                            )}
                        </p>

                        ${
                            panel.dialogue
                            ?
                            `
                            <p>
                                <strong>Dialogue:</strong><br>
                                ${escapeHtml(
                                    panel.dialogue
                                )}
                            </p>
                            `
                            :
                            ""
                        }

                        ${
                            panel.image_error
                            ?
                            `
                            <p style="color:red">
                                Image error:
                                ${escapeHtml(
                                    panel.image_error
                                )}
                            </p>
                            `
                            :
                            ""
                        }

                    </div>
                </div>
            `;
        });

        html += `</div>`;

        resultBox.innerHTML = html;

        resultBox.scrollIntoView({
            behavior: "smooth"
        });
    }


    function escapeHtml(value) {

        const div =
            document.createElement("div");

        div.textContent =
            String(value ?? "");

        return div.innerHTML;
    }

});