exports.handler = async function(event, context) {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method Not Allowed" };
  }

  try {
    const { query, language } = JSON.parse(event.body);
    const API_KEY = process.env.GEMINI_API_KEY;

    if (!API_KEY) {
      return {
        statusCode: 500,
        body: JSON.stringify({ error: "GEMINI_API_KEY is not set in Netlify environment variables." })
      };
    }

    const prompt = `
    You are a friendly, witty, all-knowing AI Doctor and Science Explainer.
    Answer ANY question the user asks:
    - Symptoms, curious body questions ('why do we yawn?'), food facts, or science questions.
    
    Language: ${language}.
    Return strictly a JSON object with this exact schema:
    {
      "title_en": "English title",
      "title_ta": "Tamil title (தமிழ்)",
      "answer": "Simple, crisp, entertaining 2-sentence answer in ${language}",
      "why_it_happens": ["Biological/scientific cause 1 in ${language}", "Cause 2 in ${language}"],
      "fun_fact_or_tip": "1 fun fact or health tip in ${language}",
      "youtube_search": "exact search query for youtube video"
    }
    User question: "${query}"
    Output ONLY valid JSON.
    `;

    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${API_KEY}`;

    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: { responseMimeType: "application/json" }
      })
    });

    const data = await response.json();
    const rawText = data.candidates[0].content.parts[0].text;
    const parsed = JSON.parse(rawText);

    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(parsed)
    };

  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
};
