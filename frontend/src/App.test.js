import { render, screen } from '@testing-library/react';
import App from './app';

test('renders main navigation', () => {
  render(<App />);
  expect(screen.getByText(/eventmind/i)).toBeInTheDocument();
});
