import { Suspense } from 'react';

function withSuspense(Component: React.ComponentType) {
  return (
    <Suspense fallback={<span>Загрузка компонента! ... </span>}>
      <Component />
    </Suspense>
  );
}

export default withSuspense;
