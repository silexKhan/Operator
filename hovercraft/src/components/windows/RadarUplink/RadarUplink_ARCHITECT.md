# RadarUplink Architect

## Equation (방정식)
`RadarUplink = lim(t→∞) ∑(Signal_i * Position_i)`
> "모든 신호와 위치의 합이 무한한 시간에 수렴할 때, 전술 지도는 완성된다."

## TDD Fences (울타리)
1. **Visualization Only**: 지도는 오직 데이터를 시각화할 뿐, 원본 데이터를 수정하지 않는다.
2. **Coordinate Integrity**: 좌표 정보는 읽기 전용으로 취급한다.
3. **UI Purity**: CSS 애니메이션(`animate-pulse`)과 SVG/Canvas 요소는 성능 최적화를 위해 내부적으로 관리한다.
4. **Independent Scanning**: 스캔 입력창의 데이터는 다른 윈도우의 필터링에 영향을 주지 않는다.
