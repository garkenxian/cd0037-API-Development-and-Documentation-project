# React Component Changes for New API Design

## Overview
The React frontend must be updated to work with the new persistent game session architecture. This document outlines required changes to each component.

---

## Key Changes Summary

| Component | Current | New | Impact |
|-----------|---------|-----|--------|
| **QuizView** | Stateless, client-side validation | Session-based, server validation | Major rewrite |
| **App** | No user selection | User select/create | New flow |
| **FormView** | No changes needed | No changes needed | None |
| **Search** | No changes needed | No changes needed | None |
| **QuestionView** | No changes needed | No changes needed | None |
| **Header** | No changes needed | Add user display | Minor |
| **New** | N/A | User dashboard | New |
| **New** | N/A | Leaderboard | New |

---

## 1. App.js (Entry Point)

### Current State
- Routes between QuestionView, FormView, QuizView, Search
- No user context
- No user selection before game

### Changes Needed

**Add User Context/State:**
```javascript
const [currentUser, setCurrentUser] = useState(null);
const [users, setUsers] = useState([]);
```

**New Flow:**
1. On app load: Check if user exists (GET /users)
2. Show user selection/creation dialog
3. Set currentUser in state/context
4. Pass currentUser to QuizView + other components
5. Allow changing user (logout equivalent)

**Components to Update:**
- Pass `currentUser` prop to QuizView
- Pass `setCurrentUser` callback to user selection modal
- Display current user in header

### API Calls
- GET /users (on app mount)
- POST /users (create new user)
- GET /users/<id> (get user details for profile)

---

## 2. QuizView.js (Major Rewrite)

### Current State
- Questions fetched via GET /quizzes (returns with answer)
- Answer validated locally via `evaluateAnswer()`
- Score tracked in React state
- Displays answer after submit

### New Architecture Required

**State Needed:**
```javascript
const [quizSessionId, setQuizSessionId] = useState(null);
const [currentQuestion, setCurrentQuestion] = useState(null);
const [currentScore, setCurrentScore] = useState({
  correct: 0,
  total_answered: 0,
  total_questions: 0
});
const [userAnswer, setUserAnswer] = useState('');
const [quizStarted, setQuizStarted] = useState(false);
const [quizCompleted, setQuizCompleted] = useState(false);
const [feedback, setFeedback] = useState(null); // correct/incorrect + answer
```

**Component Lifecycle:**

#### Phase 1: Category Selection
```javascript
selectCategory = ({ type, id = 0 }) => {
  // Call POST /games
  POST /games {
    user_id: currentUser.id,
    category_id: id,
    number_of_questions: 5
  }
  // Response: {quiz_session_id, question_number, current_score, question}
  // Store quiz_session_id, set currentQuestion, update currentScore
}
```

#### Phase 2: Answer Question
```javascript
submitGuess = (event) => {
  event.preventDefault();
  
  // POST /games/{game_session_id}/{question_number}
  POST /games/42/1 {
    user_answer: userAnswer
  }
  
  // Response: {correct, correct_answer, current_score, question_number, question}
  // Show feedback: "Correct! The answer is H2O"
  // Update currentScore
  // If question is null -> quizCompleted = true
  // If question exists -> set currentQuestion to next question
}
```

#### Phase 3: Quiz Completion
- When question is null, show final score
- Display: "You got 4 out of 5 correct (80%)"
- Button to "Play Again" (reset state)
- Button to "View Profile" (go to user page)

#### Phase 4: Recovery/Catch-Up (Optional)
```javascript
// On mount or if connection lost
GET /games/42
// Returns current state + next unanswered question
// Allow user to continue from where they left off
```

**Key Changes:**
- ❌ Remove local answer validation (`evaluateAnswer()`)
- ❌ Remove showing answer in UI during quiz
- ✅ Show feedback after server validation
- ✅ Server-side score is authoritative (use from API response)
- Session-based game (game_session_id persisted)
- Connection recovery (GET /games/<id> if needed)

### API Calls
- GET /categories (on mount)
- POST /games (start game)
- POST /games/<id>/<num> (answer question, loop)
- GET /games/<id> (optional: catch-up)

---

## 3. Header.js (Minor Update)

### Current State
- Displays title/logo
- Logout button (though no real auth)

### Changes Needed
- Display current user: "Playing as: alice_wonder"
- Add button to switch user (calls logout/setCurrentUser(null))
- Maybe link to user profile/leaderboard

### API Calls
- None (uses currentUser from App context)

---

## 4. QuestionView.js (No Changes)

### Current State
- Displays list of questions by category
- Delete button for each question

### Changes Needed
- None - existing endpoints still work
- GET /categories/<id>/questions (unchanged)
- DELETE /questions/<id> (unchanged)

### API Calls
- None new

---

## 5. FormView.js (No Changes)

### Current State
- Form to add new question
- POST /questions (create)

### Changes Needed
- None - existing endpoint still works
- POST /questions (unchanged format)

### API Calls
- None new

---

## 6. Search.js (No Changes)

### Current State
- Search bar
- GET /questions?search=term (existing)

### Changes Needed
- None - search moved from POST to GET query param (already done)
- GET /questions?search=searchTerm (unchanged)

### API Calls
- None new

---

## 7. NEW: UserDashboard.js (New Component)

### Purpose
Show user stats and game history

### Component Structure
```javascript
const UserDashboard = ({ userId }) => {
  const [user, setUser] = useState(null);
  const [gameHistory, setGameHistory] = useState([]);
  
  useEffect(() => {
    // GET /users/{userId}
    // Response: {id, username, total_score, games_played, game_sessions: [...]}
  }, [userId]);
  
  return (
    <div>
      <h2>{user.username}</h2>
      <p>Total Score: {user.total_score}</p>
      <p>Games Played: {user.games_played}</p>
      <table>
        {gameHistory.map(game => (
          <tr>
            <td>{game.quiz_category_type}</td>
            <td>{game.score}</td>
            <td>{game.correct_answers}/{game.questions_answered}</td>
            <td>{game.date_played}</td>
          </tr>
        ))}
      </table>
    </div>
  );
};
```

### API Calls
- GET /users/<id> (fetch user + game history)

---

## 8. NEW: Leaderboard.js (New Component)

### Purpose
Show top users by score

### Component Structure
```javascript
const Leaderboard = () => {
  const [leaderboard, setLeaderboard] = useState([]);
  
  useEffect(() => {
    // GET /leaderboard?limit=20
    // Response: {leaderboard: [{rank, id, username, total_score, games_played}, ...]}
  }, []);
  
  return (
    <table>
      <thead>
        <tr>
          <th>Rank</th>
          <th>Username</th>
          <th>Total Score</th>
          <th>Games Played</th>
        </tr>
      </thead>
      <tbody>
        {leaderboard.map(user => (
          <tr>
            <td>{user.rank}</td>
            <td>{user.username}</td>
            <td>{user.total_score}</td>
            <td>{user.games_played}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};
```

### API Calls
- GET /leaderboard (fetch top users)

---

## 9. NEW: UserSelector.js (New Component)

### Purpose
Modal/view to select or create user before playing quiz

### Component Structure
```javascript
const UserSelector = ({ onUserSelect }) => {
  const [users, setUsers] = useState([]);
  const [newUsername, setNewUsername] = useState('');
  const [mode, setMode] = useState('select'); // or 'create'
  
  useEffect(() => {
    // GET /users
    // Response: {users: [{id, username, total_score, games_played}, ...]}
  }, []);
  
  const handleSelectUser = (userId) => {
    onUserSelect(userId);
  };
  
  const handleCreateUser = () => {
    // POST /users {username: newUsername}
    // Response: {id, username, ...}
    // onUserSelect(response.id);
  };
  
  return (
    <div>
      {mode === 'select' ? (
        <>
          <h2>Select Player</h2>
          <ul>
            {users.map(user => (
              <li key={user.id} onClick={() => handleSelectUser(user.id)}>
                {user.username}
              </li>
            ))}
          </ul>
          <button onClick={() => setMode('create')}>Create New Player</button>
        </>
      ) : (
        <>
          <h2>Create New Player</h2>
          <input 
            value={newUsername} 
            onChange={e => setNewUsername(e.target.value)}
            placeholder="Username"
          />
          <button onClick={handleCreateUser}>Create</button>
          <button onClick={() => setMode('select')}>Back</button>
        </>
      )}
    </div>
  );
};
```

### API Calls
- GET /users (fetch users on mount)
- POST /users (create new user)

---

## Updated App.js Flow

```javascript
function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [showUserSelector, setShowUserSelector] = useState(true);
  
  if (!currentUser) {
    return <UserSelector onUserSelect={(user) => {
      // Store the full user object (or fetch it before setting state)
      setCurrentUser(user);
      setShowUserSelector(false);
    }} />;
  }
  
  return (
    <>
      <Header currentUser={currentUser} onLogout={() => setCurrentUser(null)} />
      <main>
        <nav>
          <Link to="/quiz">Play</Link>
          <Link to="/questions">Questions</Link>
          <Link to="/profile">My Profile</Link>
          <Link to="/leaderboard">Leaderboard</Link>
        </nav>
        <Routes>
          <Route path="/quiz" element={<QuizView currentUser={currentUser} />} />
          <Route path="/questions" element={<QuestionView />} />
          <Route path="/add" element={<FormView />} />
          <Route path="/search" element={<Search />} />
          <Route path="/profile" element={<UserDashboard userId={currentUser.id} />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
        </Routes>
      </main>
    </>
  );
}
```

---

## Component Changes Summary

| Component | Type | Changes |
|-----------|------|---------|
| App.js | Update | Add user selection, context |
| QuizView.js | **Major Rewrite** | Session-based, server validation |
| Header.js | Update | Display current user |
| FormView.js | No change | ✅ Existing API still works |
| QuestionView.js | No change | ✅ Existing API still works |
| Search.js | No change | ✅ Existing API still works |
| UserSelector.js | **New** | User select/create modal |
| UserDashboard.js | **New** | User profile + game history |
| Leaderboard.js | **New** | Top users by score |

---

## New API Calls Required (Frontend)

### Users
- GET /users (UserSelector.js, App.js)
- POST /users (UserSelector.js)
- GET /users/<id> (UserDashboard.js)

### Categories
- GET /categories (QuizView.js - already doing this)

### Quiz
- POST /games (QuizView.js - create session)
- POST /games/<id>/<num> (QuizView.js - answer question)
- GET /games/<id> (QuizView.js - optional catch-up)

### Leaderboard
- GET /leaderboard (Leaderboard.js)

### Existing (No Changes)
- GET /questions (Search.js, unchanged)
- GET /categories/<id>/questions (QuestionView.js, unchanged)
- DELETE /questions/<id> (QuestionView.js, unchanged)
- POST /questions (FormView.js, unchanged)

---

## Testing Strategy (Frontend)

### QuizView Component Tests
1. ✅ Renders user selection before quiz
2. ✅ POST /games creates session and displays first question
3. ✅ Question does NOT show answer
4. ✅ POST /games/<game_session_id>/<question_number> validates and shows feedback
5. ✅ Quiz completes when final question answered
6. ✅ Score calculated correctly from API response

### UserDashboard Component Tests
1. ✅ GET /users/<id> fetches and displays user stats
2. ✅ Game history shows correct sessions
3. ✅ Dates/scores display correctly

### Leaderboard Component Tests
1. ✅ GET /leaderboard fetches top users
2. ✅ Ranking displays correctly
3. ✅ Sort order correct (highest score first)

### UserSelector Component Tests
1. ✅ GET /users displays available players
2. ✅ Can select existing user
3. ✅ POST /users creates new user
4. ✅ onUserSelect callback fires correctly

---

## Implementation Order (Frontend)

### Phase 1: User Infrastructure
1. UserSelector component (with GET /users, POST /users)
2. Update App.js to use UserSelector
3. Pass currentUser throughout app

### Phase 2: Quiz Redesign
4. Rewrite QuizView for session-based architecture
5. Remove local answer validation
6. Add server validation feedback

### Phase 3: User Features
7. UserDashboard component (GET /users/<id>)
8. Leaderboard component (GET /leaderboard)
9. Update Header to show current user

### Phase 4: Integration & Testing
10. End-to-end testing (select user → play quiz → view profile)
11. Verify all API calls work
12. Handle error cases

---

## Breaking Changes from Original

| Feature | Was | Now | Impact |
|---------|-----|-----|--------|
| Answer visibility | Visible on page | Hidden until after submit | Cheating prevention |
| Score tracking | React state | Server authoritative | Trust/validation |
| User selection | None | Required before quiz | Game identity |
| Game recovery | Not possible | GET /games/<id> | Connection resilience |
| Answer feedback | Instant (local check) | After server validation | Slight latency increase |
| Quiz sessions | Ephemeral | Persistent + auditable | Better tracking |

---

## Migration Notes

- Existing QuestionView/FormView/Search components work unchanged
- Only QuizView needs major rewrite
- New components (UserSelector, UserDashboard, Leaderboard) are additive
- Frontend tests should be updated to test new API patterns
