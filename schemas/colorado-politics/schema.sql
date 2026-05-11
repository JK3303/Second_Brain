-- ============================================================
-- Colorado Politics Schema for Open Brain
-- Adds structured tables for districts, candidates,
-- election results, campaign finance, and research notes.
-- ============================================================

-- ------------------------------------------------------------
-- Districts
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.co_districts (
  id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  name            TEXT        NOT NULL,
  type            TEXT        NOT NULL CHECK (type IN (
                                'congressional',
                                'state_senate',
                                'state_house',
                                'county_commissioner',
                                'county',
                                'school_board',
                                'municipal'
                              )),
  district_number TEXT,
  description     TEXT,
  notable_cities  TEXT[]      DEFAULT '{}',
  demographics    JSONB       DEFAULT '{}',
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------
-- Candidates
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.co_candidates (
  id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  full_name        TEXT        NOT NULL,
  party            TEXT        CHECK (party IN (
                                 'Republican', 'Democrat', 'Independent',
                                 'Libertarian', 'Green', 'Other', 'Nonpartisan'
                               )),
  office           TEXT        NOT NULL,
  district_id      UUID        REFERENCES public.co_districts(id),
  bio              TEXT,
  positions        JSONB       DEFAULT '{}',
  contact_info     JSONB       DEFAULT '{}',
  social_media     JSONB       DEFAULT '{}',
  campaign_website TEXT,
  incumbent        BOOLEAN     DEFAULT FALSE,
  active           BOOLEAN     DEFAULT TRUE,
  sources          JSONB       DEFAULT '[]',
  created_at       TIMESTAMPTZ DEFAULT NOW(),
  updated_at       TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------
-- Election Results
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.co_election_results (
  id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  district_id      UUID        REFERENCES public.co_districts(id),
  candidate_id     UUID        REFERENCES public.co_candidates(id),
  election_year    INTEGER     NOT NULL,
  election_type    TEXT        NOT NULL CHECK (election_type IN (
                                 'primary', 'general', 'special', 'runoff'
                               )),
  votes            INTEGER,
  percentage       NUMERIC(5,2),
  won              BOOLEAN,
  total_votes_cast INTEGER,
  source_url       TEXT,
  created_at       TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------
-- Campaign Finance
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.co_campaign_finance (
  id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_id  UUID        REFERENCES public.co_candidates(id),
  cycle_year    INTEGER     NOT NULL,
  total_raised  NUMERIC(14,2),
  total_spent   NUMERIC(14,2),
  cash_on_hand  NUMERIC(14,2),
  top_donors    JSONB       DEFAULT '[]',
  source        TEXT,
  source_url    TEXT,
  last_updated  TIMESTAMPTZ DEFAULT NOW(),
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------
-- Research Notes — links Open Brain thoughts to political entities
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.co_research_notes (
  id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  thought_id   UUID        REFERENCES public.thoughts(id) ON DELETE CASCADE,
  subject_type TEXT        NOT NULL CHECK (subject_type IN (
                             'candidate', 'district', 'election', 'policy', 'general'
                           )),
  candidate_id UUID        REFERENCES public.co_candidates(id),
  district_id  UUID        REFERENCES public.co_districts(id),
  tags         TEXT[]      DEFAULT '{}',
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------
-- Indexes
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_co_candidates_district    ON public.co_candidates(district_id);
CREATE INDEX IF NOT EXISTS idx_co_candidates_party       ON public.co_candidates(party);
CREATE INDEX IF NOT EXISTS idx_co_candidates_active      ON public.co_candidates(active);
CREATE INDEX IF NOT EXISTS idx_co_election_results_year  ON public.co_election_results(election_year);
CREATE INDEX IF NOT EXISTS idx_co_election_results_cand  ON public.co_election_results(candidate_id);
CREATE INDEX IF NOT EXISTS idx_co_finance_candidate      ON public.co_campaign_finance(candidate_id);
CREATE INDEX IF NOT EXISTS idx_co_research_thought       ON public.co_research_notes(thought_id);
CREATE INDEX IF NOT EXISTS idx_co_research_candidate     ON public.co_research_notes(candidate_id);

-- ------------------------------------------------------------
-- Permissions — required on new Supabase projects
-- ------------------------------------------------------------
GRANT SELECT, INSERT, UPDATE, DELETE ON public.co_districts         TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.co_candidates        TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.co_election_results  TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.co_campaign_finance  TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.co_research_notes    TO service_role;
