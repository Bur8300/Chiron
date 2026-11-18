import { render, screen } from '@testing-library/react'
import { expect, test } from 'vitest'

import App from '../../frontend/src/App'

test('renders the app title', () => {
  render(<App />)
  expect(screen.getByRole('heading', { name: 'Chiron' })).toBeDefined()
})
