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
    { threshold: 0.16 }
);

revealElements.forEach((element, index) => {
    element.style.transitionDelay = `${Math.min(index * 70, 420)}ms`;
    observer.observe(element);
});

const header = document.querySelector(".site-header");

window.addEventListener("scroll", () => {
    header.style.boxShadow = window.scrollY > 24
        ? "0 12px 30px rgba(15, 23, 42, 0.08)"
        : "none";
});

const chatBox = document.querySelector("#chatBox");
const questionForm = document.querySelector("#questionForm");
const questionInput = document.querySelector("#questionInput");
const sampleButtons = document.querySelectorAll("[data-question]");

const answers = [
    {
        keywords: ["sqlite", "store", "data", "database"],
        answer: "SQLite stores data in a single local database file. Source: sqlite.txt"
    },
    {
        keywords: ["rag", "stand", "retrieval"],
        answer: "RAG stands for Retrieval-Augmented Generation. It retrieves relevant documents before generating an answer. Source: rag.txt"
    },
    {
        keywords: ["embedding", "embeddings", "vectors"],
        answer: "Embeddings convert text into numerical vectors so similar meanings can be matched during semantic search. Source: embeddings.txt"
    }
];

function addMessage(text, type) {
    const message = document.createElement("div");
    message.className = `message ${type}-message`;
    message.textContent = text;
    chatBox.appendChild(message);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function answerQuestion(question) {
    const normalized = question.toLowerCase();
    const match = answers.find((item) =>
        item.keywords.some((keyword) => normalized.includes(keyword))
    );

    return match
        ? match.answer
        : "I could not find this information in the provided documents. In the real local app, this answer is produced by the retrieval guardrail.";
}

function submitQuestion(question) {
    const cleanQuestion = question.trim();

    if (!cleanQuestion) {
        return;
    }

    addMessage(cleanQuestion, "user");

    window.setTimeout(() => {
        addMessage(answerQuestion(cleanQuestion), "assistant");
    }, 450);

    questionInput.value = "";
}

questionForm.addEventListener("submit", (event) => {
    event.preventDefault();
    submitQuestion(questionInput.value);
});

sampleButtons.forEach((button) => {
    button.addEventListener("click", () => {
        submitQuestion(button.dataset.question);
    });
});
