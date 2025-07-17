import React, { useState, useEffect } from "react";
import { useLocation,  useNavigate  } from "react-router-dom";
function ProfilePage() {
  const navigate = useNavigate();
  const storedUser = JSON.parse(localStorage.getItem("user")) || {};
  const { user_id, email } = { user_id: storedUser.user_id, email: storedUser.email };
  const [userInfo, setUserInfo] = useState({
    user_id: user_id || "",
    name: "",
    email: email || "",
    gender: "",
    location: "",
    occupation: "",
    interests: [],
  });

  const [editMode, setEditMode] = useState(false);
  const [draftInfo, setDraftInfo] = useState(null); // draft
  const [showModal, setShowModal] = useState(false);
  const [currentPage, setCurrentPage] = useState(0);
  const [answers, setAnswers] = useState(["", "", "", "", ""]);

  // Fetch profile data and answers from the database
  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log("user_id", user_id);
        // Fetch user profile data
        const profileResponse = await fetch("http://localhost:5000/api/fetch_user_data", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id }),
        });
        const profileData = await profileResponse.json();
        console.log("profileData", localStorage.getItem("user"));
        if (profileData.status === "success" && profileData.data.length > 0) {
          const infoChunk = profileData.data; // Extract the info_chunk field
        const [name, email, gender, location, occupation, interests] = infoChunk.split(", ");
        setUserInfo({
          user_id: user_id,
          name: name || "",
          email: email,
          gender: gender || "",
          location: location || "",
          occupation: occupation || "",
          interests: interests ? interests.split(", ") : [],
        });
        }

        // Fetch user answers
        const answersResponse = await fetch("http://localhost:5000/api/fetch_user_answer", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id }),
        });
        const answersData = await answersResponse.json();
        if (answersData.status === "success" && answersData.data.length > 0) {
          setAnswers(answersData.data.map((item) => item.info_chunk));
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };


      fetchData();
 
  }, [user_id, navigate]);

  const handleChange = (key, value) => {
    setUserInfo((prev) => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    // TODO: save to database
    const response = await fetch("http://localhost:5000/api/save_user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(draftInfo),
    });
    const result = await response.json();

    setUserInfo(draftInfo);
    setEditMode(false);
    setDraftInfo(null);
    alert("Information saved");
  };

  const handleCancel = () => {
    setDraftInfo(null); // discard draft
    setEditMode(false);
  };

  const displayData = editMode ? draftInfo : userInfo;

  return (
    <>
      <div className="min-h-screen bg-gray-100 flex justify-center items-center p-6">
        <div className="bg-white shadow-md rounded p-6 w-full max-w-lg space-y-4">
          <h2 className="text-2xl font-bold">Personal info</h2>

          <div className="space-y-2">
            <label className="block text-sm font-medium">ID</label>
            <input
              disabled
              value={userInfo.user_id}
              className="w-full border px-3 py-2 rounded bg-gray-100"
            />
            <label className="block text-sm font-medium">Name</label>
            <input
              disabled={!editMode}
              value={editMode ? draftInfo?.name : userInfo.name}
              onChange={(e) =>
                editMode && setDraftInfo({ ...draftInfo, name: e.target.value })
              }
              className="w-full border px-3 py-2 rounded"
            />
            <label className="block text-sm font-medium">Email</label>
            <input
              disabled
              value={userInfo.email}
              className="w-full border px-3 py-2 rounded bg-gray-100"
            />

            <label className="block text-sm font-medium">Gender</label>
            <input
              disabled={!editMode}
              value={editMode ? draftInfo?.gender : userInfo.gender}
              onChange={(e) =>
                editMode &&
                setDraftInfo({ ...draftInfo, gender: e.target.value })
              }
              className="w-full border px-3 py-2 rounded"
            />

            <label className="block text-sm font-medium">Location</label>
            <input
              disabled={!editMode}
              value={editMode ? draftInfo?.location : userInfo.location}
              onChange={(e) =>
                editMode &&
                setDraftInfo({ ...draftInfo, location: e.target.value })
              }
              className="w-full border px-3 py-2 rounded"
            />

            <label className="block text-sm font-medium">Occupation</label>
            <input
              disabled={!editMode}
              value={editMode ? draftInfo?.occupation : userInfo.occupation}
              onChange={(e) =>
                editMode &&
                setDraftInfo({ ...draftInfo, occupation: e.target.value })
              }
              className="w-full border px-3 py-2 rounded"
            />

            <label className="block text-sm font-medium">Interests</label>
            <input
              disabled={!editMode}
              value={
                editMode
                  ? draftInfo?.interests?.join(", ") || ""
                  : userInfo.interests.join(", ")
              }
              onChange={(e) =>
                editMode &&
                setDraftInfo({
                  ...draftInfo,
                  interests: e.target.value.split(",").map((i) => i.trim()),
                })
              }
              className="w-full border px-3 py-2 rounded"
            />
          </div>

          <div className="pt-4 flex justify-end space-x-2">
            {editMode ? (
              <>
                <button
                  className="px-4 py-2 bg-gray-300 rounded"
                  onClick={handleCancel}
                >
                  Cancel
                </button>
                <button
                  className="px-4 py-2 bg-black text-white rounded hover:bg-gray"
                  onClick={handleSave}
                >
                  Save
                </button>
              </>
            ) : (
              <button
                className="px-4 py-2 bg-black text-white rounded hover:bg-gray"
                onClick={() => {
                  setDraftInfo({ ...userInfo });
                  setEditMode(true);
                }}
              >
                Edit
              </button>
            )}
          </div>
          <div className="pt-4 flex justify-center">
            <button
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              onClick={() => {
                setShowModal(true);
                setCurrentPage(0);
              }}
            >
              Answer More Questions to Enhance Your Personalization!
            </button>
          </div>
        </div>
      </div>
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded shadow-md w-full max-w-xl space-y-4">
            <h3 className="text-xl font-bold">
              Questionnaire (Page {currentPage + 1}/5)
            </h3>
            <div>
              {currentPage === 0 && (
                <>
                  <p>
                    Please briefly describe the type of advice or strategies you
                    prefer. For example, do you prefer high-risk, high-reward
                    strategies, or more stable and conservative ones?
                  </p>
                  <input
                    type="text"
                    value={answers[0]}
                    onChange={(e) =>
                      setAnswers((prev) => {
                        let copy = [...prev];
                        copy[0] = e.target.value;
                        return copy;
                      })
                    }
                    className="border p-2 w-full mt-2"
                  />
                  <p>
                    Briefly describe the kind of tone you prefer in
                    responses—for example, more humorous or more friendly.
                  </p>
                  <input
                    type="text"
                    value={answers[1]}
                    onChange={(e) =>
                      setAnswers((prev) => {
                        let copy = [...prev];
                        copy[1] = e.target.value;
                        return copy;
                      })
                    }
                    className="border p-2 w-full mt-2"
                  />
                  <p>
                    If you'd like me to respond to you in a certain role, what
                    kind of role would you prefer?
                  </p>
                  <input
                    type="text"
                    value={answers[2]}
                    onChange={(e) =>
                      setAnswers((prev) => {
                        let copy = [...prev];
                        copy[2] = e.target.value;
                        return copy;
                      })
                    }
                    className="border p-2 w-full mt-2"
                  />
                </>
              )}
              {currentPage === 1 && (
                <>
                  <p>
                    Briefly describe your work. If you're a student, briefly
                    describe what you're studying.
                  </p>
                  <input
                    type="text"
                    value={answers[3]}
                    onChange={(e) => {
                      let copy = [...answers];
                      copy[3] = e.target.value;
                      setAnswers(copy);
                    }}
                    className="border p-2 w-full mt-2"
                  />
                  <p>
                    Briefly describe the types of questions or topics you prefer
                    to consult a language model about.
                  </p>
                  <input
                    type="text"
                    value={answers[4]}
                    onChange={(e) => {
                      let copy = [...answers];
                      copy[4] = e.target.value;
                      setAnswers(copy);
                    }}
                    className="border p-2 w-full mt-2"
                  />
                  <p>
                    What tools, platforms, or programming languages do you
                    primarily use in your daily work or studies?
                  </p>
                  <input
                    type="text"
                    value={answers[5]}
                    onChange={(e) => {
                      let copy = [...answers];
                      copy[5] = e.target.value;
                      setAnswers(copy);
                    }}
                    className="border p-2 w-full mt-2"
                  />
                </>
              )}

              {currentPage === 2 && (
                <>
                  <p>
                    What topics or types of articles have you enjoyed reading
                    the most recently?
                  </p>
                  <input
                    type="text"
                    value={answers[6]}
                    onChange={(e) => {
                      let copy = [...answers];
                      copy[6] = e.target.value;
                      setAnswers(copy);
                    }}
                    className="border p-2 w-full mt-2"
                  />
                  <p>What is your preferred learning style?</p>
                  <input
                    type="text"
                    value={answers[7]}
                    onChange={(e) => {
                      let copy = [...answers];
                      copy[7] = e.target.value;
                      setAnswers(copy);
                    }}
                    className="border p-2 w-full mt-2"
                  />
                  <p>
                    Do you prefer rigorous theoretical explanations or
                    examples-based explanations?
                  </p>
                  <input
                    type="text"
                    value={answers[8]}
                    onChange={(e) => {
                      let copy = [...answers];
                      copy[8] = e.target.value;
                      setAnswers(copy);
                    }}
                    className="border p-2 w-full mt-2"
                  />
                </>
              )}
              {currentPage === 3 && (
                <>
                  <p>
                    Have you recently enjoyed any specific movies, books, or
                    music?
                  </p>
                  <input
                    type="text"
                    value={answers[9]}
                    onChange={(e) => {
                      let copy = [...answers];
                      copy[9] = e.target.value;
                      setAnswers(copy);
                    }}
                    className="border p-2 w-full mt-2"
                  />
                  <p>
                    Do you have any particular sports hobbies you've been into
                    recently?
                  </p>
                  <input
                    type="text"
                    value={answers[10]}
                    onChange={(e) => {
                      let copy = [...answers];
                      copy[10] = e.target.value;
                      setAnswers(copy);
                    }}
                    className="border p-2 w-full mt-2"
                  />
                  <p>
                    Is there a hobby or interest you've always wanted to try but
                    haven't yet?
                  </p>
                  <input
                    type="text"
                    value={answers[11]}
                    onChange={(e) => {
                      let copy = [...answers];
                      copy[11] = e.target.value;
                      setAnswers(copy);
                    }}
                    className="border p-2 w-full mt-2"
                  />
                </>
              )}
              {currentPage === 4 && (
                <>
                  <p>What is your current short-term goal?</p>
                  <input
                    type="text"
                    value={answers[12]}
                    onChange={(e) => {
                      let copy = [...answers];
                      copy[12] = e.target.value;
                      setAnswers(copy);
                    }}
                    className="border p-2 w-full mt-2"
                  />
                  <p>What is your current long-term goal?</p>
                  <input
                    type="text"
                    value={answers[13]}
                    onChange={(e) => {
                      let copy = [...answers];
                      copy[13] = e.target.value;
                      setAnswers(copy);
                    }}
                    className="border p-2 w-full mt-2"
                  />
                  <p>
                    What kind of outcome would make you feel that this period
                    has been truly worthwhile?
                  </p>
                  <input
                    type="text"
                    value={answers[14]}
                    onChange={(e) => {
                      let copy = [...answers];
                      copy[14] = e.target.value;
                      setAnswers(copy);
                    }}
                    className="border p-2 w-full mt-2"
                  />
                </>
              )}
            </div>

            <div className="flex justify-between pt-4">
              <button
                disabled={currentPage === 0}
                onClick={() => setCurrentPage((p) => p - 1)}
                className={`px-4 py-2 rounded ${
                  currentPage === 0 ? "bg-gray-300" : "bg-gray-500 text-white"
                }`}
              >
                &lt;-
              </button>

              <button
                onClick={async () => {
                  if (currentPage === 4) {
                    for (let i = 0; i < 15; i++) {
                      const response = await fetch(
                        "http://localhost:5000/api/save_answer",
                        {
                          method: "POST",
                          headers: {
                            "Content-Type": "application/json",
                          },
                          body: JSON.stringify({
                            user_id: user_id,
                            question_index: i,
                            answer: answers[i],
                          }),
                        }
                      );
                    }
                    alert("Thanks for answering the questions!");
                    setShowModal(false);
                    navigate("/chat");          
                  } else {
                    setCurrentPage((p) => p + 1);
                  }
                }}
                className="px-4 py-2 bg-gray-700 text-white rounded"
              >
                {currentPage === 4 ? "Finish" : "->"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default ProfilePage;
