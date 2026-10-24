# RELATIVE VALUE / PAIR RESEARCH

## Научная задача и собственный исследовательский вклад

OLS residuals / carry / synthetic paths. PairModel uses ordinary least squares on aligned x,y histories, storing intercept, slope, residual mean and sample standard deviation. carry_score combines expected carry with volatility and an explicit hedge correlation clamp; synthetic_rate multiplies strictly positive path conversion ratios.

## Фактический вычислительный механизм

Pair spread = y-(alpha+beta*x); z=(spread-spread_mean)/spread_std when std>0, else zero. CarryScore=(expected_carry_bps/10000)/volatility*clamp(corr_hedge,0,1). The score is a heuristic, not calibrated expected return.

## Почему этот компонент важен для единой федерации

Это отдельный специализированный компонент — источник ограниченного, объяснимого исследования или решения. Его выводы можно передавать по типизированному контракту, не делая саму модель хозяином клиентских средств или бухгалтерского результата.

## Программа воспроизводимого эксперимента

Test cointegration vs simple correlation, rolling train-only hedge ratios, reversion half-life, turnover, bid/ask and residual structural breaks. Run market-neutral baselines and fully costed chronological OOS.

## Экспериментальный протокол и измеримые результаты

Зафиксировать исходный commit, датированные входы и их SHA-256, строгий baseline, независимую валидационную и тестовую выборки, граничные случаи, стоимость вычисления и неблагоприятные сценарии. Сравнивать на одном времени и идентичном объёме ресурсов. Публиковать не только mean score, но и распределение ошибок, устойчивость, отказные сценарии и экономические издержки. Наличие исполняемых тестов и enterprise API не доказывает реальную финансовую эффективность или production deployment.

## Подтверждающие исходники

- [`src/synergy_relative_value/core.py`](../src/synergy_relative_value/core.py)
- [`src/synergy_relative_value/synergy_contracts.py`](../src/synergy_relative_value/synergy_contracts.py)
- [`tests/`](../tests/)

## Критерий следующей версии

Перейти от предметного реализованного ядра к эксперименту с отдельным воспроизводимым manifest, автоматической CI-проверкой и фактическими доказательствами из конечной интеграции. Прежняя корневая документация сохранена полностью.
