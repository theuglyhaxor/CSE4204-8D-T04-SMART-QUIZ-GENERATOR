import React, { useEffect, useState } from 'react'

const API_BASE_URL = 'http://127.0.0.1:8001/api'

function authHeader() {
  const token = localStorage.getItem('quiz_token')
  if (!token) return {}
  return { Authorization: `Token ${token}` }
}

export default function QuizList() {
  const [quizzes, setQuizzes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function load() {
      setLoading(true)
      setError('')
      try {
        const res = await fetch(`${API_BASE_URL}/quizzes/`, {
          headers: {
            'Content-Type': 'application/json',
            ...authHeader(),
          },
        })

        const text = await res.text()
        let json
        try {
          json = JSON.parse(text)
        } catch {
          // ignore
        }

        if (!res.ok) throw new Error(json?.detail || json?.error || text || `HTTP ${res.status}`)
        setQuizzes(Array.isArray(json) ? json : json?.results || [])
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  return (
    <div className="card">
      <b>Quiz List</b>
      {loading && <div style={{ marginTop: 8 }}>Loading...</div>}
      {error && <div style={{ marginTop: 8, color: 'crimson' }}>{error}</div>}

      {!loading && !error && (
        <div style={{ marginTop: 12 }}>
          {quizzes.length === 0 ? (
            <div>No quizzes found.</div>
          ) : (
            <ul>
              {quizzes.map((q) => (
                <li key={q.id}>
                  <b>{q.title}</b> <span style={{ color: '#6b7280' }}>({q.difficulty || 'N/A'})</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}

