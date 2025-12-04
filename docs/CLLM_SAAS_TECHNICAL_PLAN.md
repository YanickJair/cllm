"""
CLLM SaaS - MVP Technical Implementation Plan
==============================================

Target: Launch-ready SaaS in 4-6 weeks
Stack: FastAPI + PostgreSQL + Redis + Next.js
Goal: Self-serve product with enterprise features
"""

# ============================================================================
# ARCHITECTURE OVERVIEW
# ============================================================================

"""
┌─────────────────────────────────────────────────────────────────┐
│                    Internet / Users                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   Cloudflare CDN   │
                    │   (DDoS, Cache)    │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                            │
┌───────▼────────┐                        ┌────────▼────────┐
│  Next.js App   │                        │   FastAPI API   │
│  (Dashboard)   │◄──────────────────────►│  (Compression)  │
│  Port 3000     │    Internal API        │   Port 8000     │
└───────┬────────┘                        └────────┬────────┘
        │                                          │
        │                          ┌───────────────┼───────────────┐
        │                          │               │               │
        │                   ┌──────▼─────┐  ┌─────▼────┐  ┌──────▼─────┐
        │                   │ PostgreSQL │  │  Redis   │  │  S3/Blob   │
        │                   │   (Data)   │  │ (Cache)  │  │  (Vocabs)  │
        │                   └────────────┘  └──────────┘  └────────────┘
        │
        └──────────────────────────────────────────┐
                                                   │
                                         ┌─────────▼────────┐
                                         │   Stripe API     │
                                         │   (Billing)      │
                                         └──────────────────┘
"""

# ============================================================================
# DATABASE SCHEMA
# ============================================================================

-- migrations/001_initial_schema.sql

-- Tenants (organizations)
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    tier VARCHAR(50) NOT NULL DEFAULT 'startup', -- startup, growth, enterprise
    stripe_customer_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    settings JSONB DEFAULT '{}'::jsonb,
    monthly_token_limit INTEGER DEFAULT 10000000, -- 10M tokens
    status VARCHAR(50) DEFAULT 'active' -- active, suspended, cancelled
);

-- Users (people within tenants)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'member', -- admin, member
    created_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP,
    UNIQUE(tenant_id, email)
);

-- API Keys
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key_prefix VARCHAR(20) NOT NULL, -- First 8 chars for display
    key_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Usage Events (high-volume table)
CREATE TABLE usage_events (
    id BIGSERIAL PRIMARY KEY,
    tenant_id UUID NOT NULL,
    api_key_id UUID,
    timestamp TIMESTAMP DEFAULT NOW(),
    
    -- Input
    tokens_original INTEGER NOT NULL,
    text_type VARCHAR(50), -- prompt, transcript, document
    
    -- Compression
    tokens_compressed INTEGER NOT NULL,
    compression_ratio FLOAT NOT NULL,
    vocabulary_used VARCHAR(100) DEFAULT 'default',
    
    -- LLM call (if compress-and-call)
    llm_provider VARCHAR(50), -- claude, gpt4, gemini
    llm_model VARCHAR(100),
    llm_latency_ms INTEGER,
    
    -- Cost calculation
    cost_without_cllm_usd NUMERIC(10, 6),
    cost_with_cllm_usd NUMERIC(10, 6),
    savings_usd NUMERIC(10, 6),
    
    -- Quality
    validation_passed BOOLEAN,
    quality_score FLOAT
);

-- Partition usage_events by month for performance
CREATE INDEX idx_usage_tenant_timestamp ON usage_events(tenant_id, timestamp DESC);
CREATE INDEX idx_usage_timestamp ON usage_events(timestamp DESC);

-- Vocabularies (custom compression dictionaries)
CREATE TABLE vocabularies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(100), -- support, sales, legal, healthcare, etc.
    description TEXT,
    vocabulary JSONB NOT NULL, -- The actual compression tokens
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, name)
);

-- Billing (for usage-based pricing)
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    stripe_invoice_id VARCHAR(255),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Usage
    tokens_compressed BIGINT NOT NULL,
    base_fee_usd NUMERIC(10, 2),
    usage_fee_usd NUMERIC(10, 2),
    total_usd NUMERIC(10, 2),
    
    -- Status
    status VARCHAR(50), -- draft, open, paid, void
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

# ============================================================================
# API IMPLEMENTATION
# ============================================================================

# app/main.py
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn

from .routers import compression, analytics, auth, admin
from .core.config import settings
from .core.database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CLLM API",
    description="Compress LLM prompts by 50-70% with <5% quality loss",
    version="1.0.0"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(compression.router, prefix="/v1", tags=["compression"])
app.include_router(analytics.router, prefix="/v1/analytics", tags=["analytics"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


# ============================================================================
# COMPRESSION ROUTER
# ============================================================================

# app/routers/compression.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import time

from ..core.auth import get_current_tenant
from ..core.encoder import CLLMEncoder
from ..core.usage import track_usage
from ..models.tenant import Tenant

router = APIRouter()
encoder = CLLMEncoder()

class CompressRequest(BaseModel):
    text: str
    vocabulary: Optional[str] = "default"
    text_type: Optional[str] = "prompt"  # prompt, transcript, document
    
class CompressResponse(BaseModel):
    compressed: str
    tokens_original: int
    tokens_compressed: int
    compression_ratio: float
    tokens_saved: int
    quality_score: float
    
class CompressAndCallRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = None
    vocabulary: Optional[str] = "default"
    llm_provider: str  # claude, gpt4, gemini
    llm_model: str     # claude-sonnet-4, gpt-4-turbo, etc.
    max_tokens: int = 1000
    temperature: float = 1.0

@router.post("/compress", response_model=CompressResponse)
async def compress(
    request: CompressRequest,
    tenant: Tenant = Depends(get_current_tenant)
):
    """
    Compress text using CLLM
    
    Returns compressed text and compression statistics.
    """
    start_time = time.time()
    
    # Load vocabulary (custom or default)
    vocabulary = await encoder.load_vocabulary(
        tenant_id=tenant.id,
        vocab_name=request.vocabulary
    )
    
    # Compress
    result = encoder.compress(
        text=request.text,
        vocabulary=vocabulary
    )
    
    # Track usage
    await track_usage(
        tenant_id=tenant.id,
        tokens_original=result.tokens_original,
        tokens_compressed=result.tokens_compressed,
        text_type=request.text_type,
        vocabulary_used=request.vocabulary,
        quality_score=result.quality_score
    )
    
    # Check monthly limit
    if await check_monthly_limit_exceeded(tenant.id):
        raise HTTPException(
            status_code=429,
            detail="Monthly token limit exceeded. Please upgrade your plan."
        )
    
    return CompressResponse(
        compressed=result.compressed,
        tokens_original=result.tokens_original,
        tokens_compressed=result.tokens_compressed,
        compression_ratio=result.compression_ratio,
        tokens_saved=result.tokens_saved,
        quality_score=result.quality_score
    )


@router.post("/compress-and-call")
async def compress_and_call(
    request: CompressAndCallRequest,
    tenant: Tenant = Depends(get_current_tenant)
):
    """
    Compress prompt and call LLM API
    
    This is a convenience endpoint that:
    1. Compresses the prompt
    2. Calls the LLM API
    3. Returns the response
    4. Tracks usage and cost savings
    """
    # Load vocabulary
    vocabulary = await encoder.load_vocabulary(
        tenant_id=tenant.id,
        vocab_name=request.vocabulary
    )
    
    # Compress system prompt if provided
    if request.system_prompt:
        compressed_system = encoder.compress(
            text=request.system_prompt,
            vocabulary=vocabulary
        )
    
    # Compress user prompt
    compressed_prompt = encoder.compress(
        text=request.prompt,
        vocabulary=vocabulary
    )
    
    # Calculate cost without CLLM
    cost_without = calculate_cost(
        provider=request.llm_provider,
        model=request.llm_model,
        input_tokens=compressed_prompt.tokens_original,
        output_tokens=request.max_tokens
    )
    
    # Call LLM
    llm_start = time.time()
    
    if request.llm_provider == "claude":
        response = await call_claude(
            system=compressed_system.compressed if request.system_prompt else None,
            prompt=compressed_prompt.compressed,
            model=request.llm_model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
    elif request.llm_provider == "gpt4":
        response = await call_openai(
            system=compressed_system.compressed if request.system_prompt else None,
            prompt=compressed_prompt.compressed,
            model=request.llm_model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
    else:
        raise HTTPException(400, f"Unsupported provider: {request.llm_provider}")
    
    llm_latency = (time.time() - llm_start) * 1000
    
    # Calculate actual cost with CLLM
    cost_with = calculate_cost(
        provider=request.llm_provider,
        model=request.llm_model,
        input_tokens=compressed_prompt.tokens_compressed,
        output_tokens=response.usage.output_tokens
    )
    
    # Track usage with cost savings
    await track_usage(
        tenant_id=tenant.id,
        tokens_original=compressed_prompt.tokens_original,
        tokens_compressed=compressed_prompt.tokens_compressed,
        llm_provider=request.llm_provider,
        llm_model=request.llm_model,
        llm_latency_ms=llm_latency,
        cost_without_cllm_usd=cost_without,
        cost_with_cllm_usd=cost_with,
        savings_usd=cost_without - cost_with,
        quality_score=compressed_prompt.quality_score
    )
    
    return {
        "response": response.content,
        "usage": {
            "original_tokens": compressed_prompt.tokens_original,
            "compressed_tokens": compressed_prompt.tokens_compressed,
            "output_tokens": response.usage.output_tokens,
            "compression_ratio": compressed_prompt.compression_ratio
        },
        "cost": {
            "without_cllm_usd": float(cost_without),
            "with_cllm_usd": float(cost_with),
            "savings_usd": float(cost_without - cost_with),
            "savings_percent": ((cost_without - cost_with) / cost_without) * 100
        },
        "latency_ms": llm_latency
    }


# ============================================================================
# ANALYTICS ROUTER
# ============================================================================

# app/routers/analytics.py
from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from typing import Optional

from ..core.auth import get_current_tenant
from ..models.tenant import Tenant
from ..core.database import get_db

router = APIRouter()

@router.get("/savings")
async def get_savings(
    period: Optional[str] = "30d",  # 7d, 30d, 90d, all
    tenant: Tenant = Depends(get_current_tenant),
    db = Depends(get_db)
):
    """
    Get savings summary for tenant
    """
    # Calculate date range
    if period == "7d":
        start_date = datetime.now() - timedelta(days=7)
    elif period == "30d":
        start_date = datetime.now() - timedelta(days=30)
    elif period == "90d":
        start_date = datetime.now() - timedelta(days=90)
    else:
        start_date = None
    
    # Query usage
    query = """
        SELECT 
            COUNT(*) as total_requests,
            SUM(tokens_original) as total_original_tokens,
            SUM(tokens_compressed) as total_compressed_tokens,
            AVG(compression_ratio) as avg_compression_ratio,
            SUM(savings_usd) as total_savings_usd,
            SUM(cost_with_cllm_usd) as total_cost_usd
        FROM usage_events
        WHERE tenant_id = :tenant_id
    """
    
    if start_date:
        query += " AND timestamp >= :start_date"
    
    result = await db.execute(query, {
        "tenant_id": tenant.id,
        "start_date": start_date
    })
    
    row = result.fetchone()
    
    return {
        "period": period,
        "total_requests": row.total_requests or 0,
        "tokens": {
            "original": row.total_original_tokens or 0,
            "compressed": row.total_compressed_tokens or 0,
            "saved": (row.total_original_tokens or 0) - (row.total_compressed_tokens or 0)
        },
        "compression_ratio": float(row.avg_compression_ratio or 0),
        "cost": {
            "with_cllm_usd": float(row.total_cost_usd or 0),
            "savings_usd": float(row.total_savings_usd or 0),
            "savings_percent": (
                (float(row.total_savings_usd) / (float(row.total_savings_usd) + float(row.total_cost_usd))) * 100
                if row.total_savings_usd and row.total_cost_usd
                else 0
            )
        }
    }


@router.get("/usage-over-time")
async def get_usage_over_time(
    period: Optional[str] = "30d",
    granularity: Optional[str] = "day",  # hour, day, week, month
    tenant: Tenant = Depends(get_current_tenant),
    db = Depends(get_db)
):
    """
    Get usage over time for charts
    """
    # Calculate date range
    if period == "7d":
        start_date = datetime.now() - timedelta(days=7)
    elif period == "30d":
        start_date = datetime.now() - timedelta(days=30)
    elif period == "90d":
        start_date = datetime.now() - timedelta(days=90)
    
    # Query with time bucketing
    if granularity == "day":
        time_bucket = "DATE(timestamp)"
    elif granularity == "hour":
        time_bucket = "DATE_TRUNC('hour', timestamp)"
    elif granularity == "week":
        time_bucket = "DATE_TRUNC('week', timestamp)"
    else:
        time_bucket = "DATE_TRUNC('month', timestamp)"
    
    query = f"""
        SELECT 
            {time_bucket} as time_bucket,
            COUNT(*) as requests,
            SUM(tokens_original) as tokens_original,
            SUM(tokens_compressed) as tokens_compressed,
            AVG(compression_ratio) as compression_ratio,
            SUM(savings_usd) as savings_usd
        FROM usage_events
        WHERE tenant_id = :tenant_id
          AND timestamp >= :start_date
        GROUP BY time_bucket
        ORDER BY time_bucket
    """
    
    result = await db.execute(query, {
        "tenant_id": tenant.id,
        "start_date": start_date
    })
    
    data = []
    for row in result.fetchall():
        data.append({
            "timestamp": row.time_bucket.isoformat(),
            "requests": row.requests,
            "tokens_original": row.tokens_original,
            "tokens_compressed": row.tokens_compressed,
            "compression_ratio": float(row.compression_ratio),
            "savings_usd": float(row.savings_usd)
        })
    
    return {"data": data}


# ============================================================================
# FRONTEND DASHBOARD
# ============================================================================

// dashboard/pages/dashboard.tsx
import { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function Dashboard() {
  const [savings, setSavings] = useState(null)
  const [usageData, setUsageData] = useState([])
  
  useEffect(() => {
    // Fetch savings
    fetch('/api/v1/analytics/savings?period=30d', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
      .then(res => res.json())
      .then(setSavings)
    
    // Fetch usage over time
    fetch('/api/v1/analytics/usage-over-time?period=30d&granularity=day', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
      .then(res => res.json())
      .then(data => setUsageData(data.data))
  }, [])
  
  if (!savings) return <div>Loading...</div>
  
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8">CLLM Dashboard</h1>
      
      {/* Savings Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardHeader>
            <CardTitle>Total Savings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">
              ${savings.cost.savings_usd.toFixed(2)}
            </div>
            <div className="text-sm text-gray-600">
              {savings.cost.savings_percent.toFixed(1)}% saved
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Tokens Saved</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {(savings.tokens.saved / 1000000).toFixed(1)}M
            </div>
            <div className="text-sm text-gray-600">
              {savings.compression_ratio.toFixed(1)}% compression
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Total Requests</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {savings.total_requests.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">
              Last 30 days
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Current Spend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              ${savings.cost.with_cllm_usd.toFixed(2)}
            </div>
            <div className="text-sm text-gray-600">
              With CLLM
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Usage Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Token Usage Over Time</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={usageData}>
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="tokens_original" 
                stroke="#8884d8" 
                name="Original"
              />
              <Line 
                type="monotone" 
                dataKey="tokens_compressed" 
                stroke="#82ca9d" 
                name="Compressed"
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  )
}


# ============================================================================
# DEPLOYMENT
# ============================================================================

# docker-compose.yml
version: '3.8'

services:
  api:
    build: ./api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://cllm:password@postgres:5432/cllm
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=${JWT_SECRET}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
    depends_on:
      - postgres
      - redis
  
  dashboard:
    build: ./dashboard
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://api:8000
  
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=cllm
      - POSTGRES_USER=cllm
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:

# ============================================================================
# 4-WEEK MVP TIMELINE
# ============================================================================

"""
WEEK 1: Core Infrastructure
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Day 1-2: Database & Auth
  - [ ] PostgreSQL schema
  - [ ] User/tenant models
  - [ ] JWT authentication
  - [ ] API key generation

Day 3-4: Compression API
  - [ ] /v1/compress endpoint
  - [ ] Integrate existing CLLM encoder
  - [ ] Usage tracking
  - [ ] Rate limiting

Day 5-7: LLM Integration
  - [ ] /v1/compress-and-call endpoint
  - [ ] Claude API integration
  - [ ] GPT-4 API integration
  - [ ] Cost calculation


WEEK 2: Dashboard & Analytics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Day 8-10: Frontend Setup
  - [ ] Next.js project
  - [ ] Authentication UI
  - [ ] Dashboard layout
  - [ ] API integration

Day 11-12: Analytics Views
  - [ ] Savings dashboard
  - [ ] Usage charts
  - [ ] Token breakdown
  - [ ] Cost visualization

Day 13-14: API Key Management
  - [ ] Create/revoke keys UI
  - [ ] Usage by key
  - [ ] Key permissions


WEEK 3: Billing & Polish
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Day 15-17: Stripe Integration
  - [ ] Stripe customer creation
  - [ ] Usage-based pricing
  - [ ] Invoice generation
  - [ ] Payment UI

Day 18-19: Documentation
  - [ ] API docs (OpenAPI)
  - [ ] Integration guide
  - [ ] Code examples
  - [ ] Video tutorial

Day 20-21: Testing & QA
  - [ ] Integration tests
  - [ ] Load testing
  - [ ] Security audit
  - [ ] Bug fixes


WEEK 4: Launch Prep
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Day 22-24: Deployment
  - [ ] Production environment
  - [ ] CI/CD pipeline
  - [ ] Monitoring setup
  - [ ] Backup strategy

Day 25-26: Marketing Assets
  - [ ] Landing page
  - [ ] Pitch deck
  - [ ] Demo video
  - [ ] Case studies

Day 27-28: Soft Launch
  - [ ] Onboard first 3 customers
  - [ ] Collect feedback
  - [ ] Fix issues
  - [ ] Prepare for public launch
"""

# ============================================================================
# COST STRUCTURE
# ============================================================================

"""
Monthly Operating Costs (MVP):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Infrastructure:
  AWS/GCP hosting           $200
  PostgreSQL (managed)      $100
  Redis (managed)           $50
  CDN (Cloudflare)          $20
  Monitoring (Datadog)      $100
  ──────────────────────────────
  Subtotal                  $470/month

Services:
  Stripe fees (2.9% + 30¢)  Variable
  LLM API (testing)         $500
  Email (SendGrid)          $20
  SMS (Twilio)              $20
  ──────────────────────────────
  Subtotal                  $540/month

Software:
  GitHub                    $0 (free)
  Figma                     $12
  Domain + SSL              $20
  ──────────────────────────────
  Subtotal                  $32/month

TOTAL MONTHLY              ~$1,042/month
TOTAL ANNUAL               ~$12,500/year

Break-even: 3-4 paying customers at $499/month
"""

# ============================================================================
# SUCCESS METRICS
# ============================================================================

"""
MVP Success Criteria:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Technical:
  ✓ API latency <100ms (p95)
  ✓ Uptime >99.5%
  ✓ Compression ratio >60%
  ✓ Quality score >90%
  
Business:
  ✓ 10 beta customers signed up
  ✓ 5 paying customers
  ✓ $2,500 MRR
  ✓ <10% churn
  
Product:
  ✓ <5 critical bugs
  ✓ NPS >40
  ✓ 80% feature adoption
  ✓ <24hr time to first value
"""
