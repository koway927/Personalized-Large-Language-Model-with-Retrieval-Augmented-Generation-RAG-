const apiKey = process.env.REACT_APP_GEMINI_API_KEY;
const model = "gemini-1.5-flash"; 

export async function extractInfoFromQuery(query) {
  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          contents: [
            {
              parts: [
                {
                  text: `You are an assistant that extracts structured information from natural language queries.

Extract the following:
- interest: What general area or domain does this question relate to? (e.g., history, science, politics)
- topic: What is the main entity or subject being asked about?
- question_type: What type of question is this? (e.g., factual, opinion, comparison, definition)
- user_goal: What is the user likely trying to achieve with this query? (e.g., learning, writing a report, casual curiosity)

Return as a JSON object.

Query: "${query}"`,
                },
              ],
            },
          ],
        }),
      }
    );

    const data = await response.json();
    const rawText = data.candidates?.[0]?.content?.parts?.[0]?.text || "{}";
    
    const cleaned = rawText.replace(/```json|```/g, "").trim();

    const info = JSON.parse(cleaned);
    return info;
  } catch (err) {
    console.error("Failed to extract info from Gemini:", err);
    return null;
  }
}
