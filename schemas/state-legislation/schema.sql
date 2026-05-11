-- ============================================================
-- State Legislation Schema for Open Brain
-- Tracks legislation across all 50 US states with topic
-- categorization, impact assessments, and news source links.
-- ============================================================

-- ------------------------------------------------------------
-- States
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.sl_states (
  id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  name         TEXT        NOT NULL UNIQUE,
  abbreviation CHAR(2)     NOT NULL UNIQUE,
  region       TEXT        CHECK (region IN (
                             'Northeast', 'Southeast', 'Midwest',
                             'Southwest', 'West'
                           )),
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------
-- Topic Categories
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.sl_topics (
  id          UUID  PRIMARY KEY DEFAULT gen_random_uuid(),
  slug        TEXT  NOT NULL UNIQUE,
  label       TEXT  NOT NULL,
  description TEXT
);

-- Seed core topics
INSERT INTO public.sl_topics (slug, label, description) VALUES
  ('healthcare',       'Healthcare Reform',       'Insurance coverage, Medicaid expansion, prescription drug pricing, mental health'),
  ('housing',          'Housing',                 'Affordable housing, zoning reform, rent control, homelessness'),
  ('jobs',             'Job Growth & Economy',    'Minimum wage, workforce development, small business, economic development'),
  ('education',        'Education',               'K-12 funding, higher education, school choice, curriculum'),
  ('criminal-justice', 'Criminal Justice',        'Policing, sentencing reform, incarceration, reentry programs'),
  ('environment',      'Environment & Energy',    'Climate policy, renewable energy, clean air/water, land use'),
  ('taxes',            'Taxes & Budget',          'Income tax, property tax, budget policy, fiscal reform'),
  ('infrastructure',   'Infrastructure',          'Roads, broadband, public transit, utilities'),
  ('immigration',      'Immigration',             'State-level immigration enforcement, sanctuary policies, ID laws'),
  ('voting',           'Voting & Elections',      'Voter ID, ballot access, redistricting, election administration')
ON CONFLICT (slug) DO NOTHING;

-- ------------------------------------------------------------
-- Legislation
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.sl_legislation (
  id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  state_id         UUID        REFERENCES public.sl_states(id),
  bill_number      TEXT,
  title            TEXT        NOT NULL,
  summary          TEXT,
  full_text_url    TEXT,
  status           TEXT        NOT NULL CHECK (status IN (
                                 'introduced', 'in_committee', 'passed_chamber',
                                 'passed', 'signed', 'vetoed', 'failed'
                               )),
  session_year     INTEGER,
  introduced_date  DATE,
  passed_date      DATE,
  signed_date      DATE,
  sponsor          TEXT,
  sponsor_party    TEXT,
  legiscan_id      INTEGER     UNIQUE,
  openstates_id    TEXT        UNIQUE,
  sources          JSONB       DEFAULT '[]',
  created_at       TIMESTAMPTZ DEFAULT NOW(),
  updated_at       TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------
-- Legislation ↔ Topics (many-to-many)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.sl_legislation_topics (
  legislation_id UUID REFERENCES public.sl_legislation(id) ON DELETE CASCADE,
  topic_id       UUID REFERENCES public.sl_topics(id)      ON DELETE CASCADE,
  PRIMARY KEY (legislation_id, topic_id)
);

-- ------------------------------------------------------------
-- Impact Assessments
-- Tracks whether a bill has had positive, negative, or mixed
-- real-world outcomes based on news and official reporting.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.sl_impact_assessments (
  id             UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  legislation_id UUID        REFERENCES public.sl_legislation(id) ON DELETE CASCADE,
  verdict        TEXT        CHECK (verdict IN ('positive', 'negative', 'mixed', 'unclear')),
  summary        TEXT,
  evidence       JSONB       DEFAULT '[]',  -- array of {source, url, excerpt, sentiment}
  assessed_by    TEXT        DEFAULT 'claude',
  assessed_at    TIMESTAMPTZ DEFAULT NOW(),
  created_at     TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------
-- News Sources
-- Articles and reports linked to specific legislation.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.sl_news_sources (
  id             UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  legislation_id UUID        REFERENCES public.sl_legislation(id) ON DELETE CASCADE,
  headline       TEXT        NOT NULL,
  outlet         TEXT,
  url            TEXT,
  published_date DATE,
  sentiment      TEXT        CHECK (sentiment IN ('positive', 'negative', 'neutral', 'mixed')),
  excerpt        TEXT,
  created_at     TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------
-- Research Notes (links to Open Brain thoughts)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.sl_research_notes (
  id             UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  thought_id     UUID        REFERENCES public.thoughts(id) ON DELETE CASCADE,
  legislation_id UUID        REFERENCES public.sl_legislation(id),
  topic_id       UUID        REFERENCES public.sl_topics(id),
  state_id       UUID        REFERENCES public.sl_states(id),
  tags           TEXT[]      DEFAULT '{}',
  created_at     TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------
-- Indexes
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_sl_legislation_state      ON public.sl_legislation(state_id);
CREATE INDEX IF NOT EXISTS idx_sl_legislation_status     ON public.sl_legislation(status);
CREATE INDEX IF NOT EXISTS idx_sl_legislation_year       ON public.sl_legislation(session_year);
CREATE INDEX IF NOT EXISTS idx_sl_leg_topics_leg         ON public.sl_legislation_topics(legislation_id);
CREATE INDEX IF NOT EXISTS idx_sl_leg_topics_topic       ON public.sl_legislation_topics(topic_id);
CREATE INDEX IF NOT EXISTS idx_sl_impact_legislation     ON public.sl_impact_assessments(legislation_id);
CREATE INDEX IF NOT EXISTS idx_sl_impact_verdict         ON public.sl_impact_assessments(verdict);
CREATE INDEX IF NOT EXISTS idx_sl_news_legislation       ON public.sl_news_sources(legislation_id);
CREATE INDEX IF NOT EXISTS idx_sl_research_thought       ON public.sl_research_notes(thought_id);

-- ------------------------------------------------------------
-- Permissions
-- ------------------------------------------------------------
GRANT SELECT, INSERT, UPDATE, DELETE ON public.sl_states               TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.sl_topics               TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.sl_legislation          TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.sl_legislation_topics   TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.sl_impact_assessments   TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.sl_news_sources         TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.sl_research_notes       TO service_role;
