import { Routes, Route } from 'react-router-dom';
import NBAList from '../components/nba/NBAList';
import NBACreate from '../components/nba/NBACreate';
import NBAEdit from '../components/nba/NBAEdit';

function NBA() {
  return (
    <Routes>
      <Route index element={<NBAList />} />
      <Route path="create" element={<NBACreate />} />
      <Route path="edit/:id" element={<NBAEdit />} />
    </Routes>
  );
}

export default NBA;
