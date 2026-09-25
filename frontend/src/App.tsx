import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import { Footer, Header } from "./components/chrome";
import { AttemptEditor } from "./pages/AttemptEditor";
import { AttemptReview } from "./pages/AttemptReview";
import { History } from "./pages/History";
import { Home } from "./pages/Home";
import { NotFound, Privacy, Terms } from "./pages/Legal";
import { ProblemDetail } from "./pages/ProblemDetail";
import { Problems } from "./pages/Problems";

export function App() {
  return (
    <BrowserRouter>
      <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:m-2 focus:rounded focus:bg-white focus:px-3 focus:py-2 focus:shadow">
        Skip to content
      </a>
      <Header />
      <main id="main" className="min-h-[60vh]">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/problems" element={<Problems />} />
          <Route path="/problems/:slug" element={<ProblemDetail />} />
          <Route path="/attempts/:id" element={<AttemptEditor />} />
          <Route path="/attempts/:id/review" element={<AttemptReview />} />
          <Route path="/history" element={<History />} />
          <Route path="/privacy" element={<Privacy />} />
          <Route path="/terms" element={<Terms />} />
          <Route
            path="*"
            element={
              <>
                <NotFound />
                <p className="sr-only">
                  <Link to="/">home</Link>
                </p>
              </>
            }
          />
        </Routes>
      </main>
      <Footer />
    </BrowserRouter>
  );
}
