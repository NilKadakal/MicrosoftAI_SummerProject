const revealElements = document.querySelectorAll(".reveal");

const observer = new IntersectionObserver(
    (entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
                observer.unobserve(entry.target);
            }
        });
    },
    { threshold: 0.14 }
);

revealElements.forEach((element, index) => {
    element.style.transitionDelay = `${Math.min(index * 55, 330)}ms`;
    observer.observe(element);
});

const chatWindow = document.querySelector("#chatWindow");
const askForm = document.querySelector("#askForm");
const questionInput = document.querySelector("#questionInput");
const fileRows = document.querySelectorAll(".file-row");
const sourceName = document.querySelector("#sourceName");

const answers = [
    {
        match: ["sqlite", "store", "database"],
        source: "sqlite.txt",
        response: "SQLite stores data in a single local database file."
    },
    {
        match: ["rag", "retrieval", "augmented"],
        source: "rag.txt",
        response: "RAG stands for Retrieval-Augmented Generation. It retrieves relevant documents before generating an answer."
    },
    {
        match: ["embedding", "embeddings", "vectors"],
        source: "embeddings.txt",
        response: "Embeddings convert text into numerical vectors so semantically similar passages can be found during retrieval."
    }
];

function addMessage(text, type) {
    const message = document.createElement("div");
    message.className = `message ${type}-message`;
    message.textContent = text;
    chatWindow.appendChild(message);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function findAnswer(question) {
    const normalized = question.toLowerCase();
    const result = answers.find((item) =>
        item.match.some((keyword) => normalized.includes(keyword))
    );

    if (!result) {
        sourceName.textContent = "No supported source";
        return "I could not find this information in the provided documents.";
    }

    sourceName.textContent = result.source;
    return `${result.response} Source: ${result.source}`;
}

function askQuestion(question) {
    const cleanQuestion = question.trim();

    if (!cleanQuestion) {
        return;
    }

    addMessage(cleanQuestion, "user");

    window.setTimeout(() => {
        addMessage(findAnswer(cleanQuestion), "assistant");
    }, 420);

    questionInput.value = "";
}

askForm.addEventListener("submit", (event) => {
    event.preventDefault();
    askQuestion(questionInput.value);
});

fileRows.forEach((row) => {
    row.addEventListener("click", () => {
        fileRows.forEach((item) => item.classList.remove("active"));
        row.classList.add("active");
        questionInput.value = row.dataset.fill;
        questionInput.focus();
    });
});
