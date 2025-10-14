import { Routes, Route } from 'react-router-dom';
import SystemPromptsList from '../components/prompts/SystemPromptsList';
import PromptEditor from '../components/prompts/PromptEditor';
import PromptTester from '../components/prompts/PromptTester';

function SystemPrompts() {
  return (
    <Routes>
      <Route index element={<SystemPromptsList />} />
      <Route path="create" element={<PromptEditor />} />
      <Route path="edit/:id" element={<PromptEditor />} />
      <Route path="test/:id" element={<PromptTester />} />
    </Routes>
  );
}
export default SystemPrompts;