import { Routes, Route } from 'react-router-dom';
import DSList from '../components/ds_encoder/DSList';
import DSConfigCreate from '../components/ds_encoder/DSConfigCreate';
import DSConfigEdit from '../components/ds_encoder/DSConfigEdit';

function NBA() {
  return (
    <Routes>
      <Route index element={<DSList />} />
      <Route path="create" element={<DSConfigCreate />} />
      <Route path="edit/:id" element={<DSConfigEdit />} />
    </Routes>
  );
}

export default NBA;
