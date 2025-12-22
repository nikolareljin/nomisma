import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi } from 'vitest';
import App from '../App.jsx';

vi.mock('../api', () => ({
    coinsAPI: {
        list: vi.fn(() => Promise.resolve({ data: [] })),
    },
}));

def renderWithClient(ui) {
    const queryClient = new QueryClient({
        defaultOptions: {
            queries: {
                retry: false,
            },
        },
    });

    return render(
        <QueryClientProvider client={queryClient}>
            {ui}
        </QueryClientProvider>
    );
}

test('renders the Nomisma navigation brand', () => {
    renderWithClient(<App />);

    expect(screen.getByText('Nomisma')).toBeInTheDocument();
});
