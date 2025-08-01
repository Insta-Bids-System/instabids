import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Shield, 
  Star, 
  Clock, 
  Users, 
  DollarSign,
  Award,
  TrendingUp,
  Target,
  Zap,
  ArrowRight,
  CheckCircle
} from 'lucide-react'
import ContractorOnboardingChat from '@/components/chat/ContractorOnboardingChat'
import { useAuth } from '@/contexts/AuthContext'

const ContractorLandingPage: React.FC = () => {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [showOnboarding, setShowOnboarding] = useState(false)
  const [sessionId] = useState(`contractor_session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)

  // If already logged in as contractor, redirect to dashboard
  React.useEffect(() => {
    const demoUser = localStorage.getItem('DEMO_USER')
    if (user && user.id) {
      navigate('/contractor/dashboard')
    } else if (demoUser) {
      const demoData = JSON.parse(demoUser)
      if (demoData.role === 'contractor') {
        navigate('/contractor/dashboard')
      }
    }
  }, [user, navigate])

  const benefits = [
    {
      icon: Shield,
      title: "Zero Lead Fees",
      description: "Submit unlimited quotes for free. Pay only when you win the job.",
      gradient: "from-green-400 to-green-600"
    },
    {
      icon: Target,
      title: "Pre-Qualified Homeowners",
      description: "Every homeowner has confirmed budget and is ready to hire immediately.",
      gradient: "from-blue-400 to-blue-600"
    },
    {
      icon: TrendingUp,
      title: "Higher Win Rates",
      description: "Our contractors average 40% higher win rates than industry standard.",
      gradient: "from-purple-400 to-purple-600"
    },
    {
      icon: Zap,
      title: "Instant Notifications",
      description: "Get notified within minutes of new projects in your area.",
      gradient: "from-yellow-400 to-yellow-600"
    }
  ]

  const stats = [
    { label: "Active Projects", value: "500+" },
    { label: "Contractor Partners", value: "10K+" },
    { label: "Projects Completed", value: "$50M+" },
    { label: "Average Win Rate", value: "40%" }
  ]

  const handleStartOnboarding = () => {
    setShowOnboarding(true)
  }

  const handleOnboardingComplete = (contractorId: string) => {
    navigate('/contractor/dashboard')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-green-500 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-pulse"></div>
      </div>

      <div className="relative z-10">
        {/* Header */}
        <header className="bg-white/10 backdrop-blur-sm border-b border-white/20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex justify-between items-center">
              <button 
                onClick={() => navigate('/')}
                className="text-2xl font-bold text-white"
              >
                Instabids
              </button>
              <nav className="flex gap-4">
                <button
                  onClick={() => navigate('/login')}
                  className="text-white/80 hover:text-white transition-colors"
                >
                  Login
                </button>
              </nav>
            </div>
          </div>
        </header>

        {!showOnboarding ? (
          <>
            {/* Hero Section */}
            <section className="pt-20 pb-16 px-4">
              <div className="max-w-7xl mx-auto text-center">
                <motion.div
                  className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-500/20 to-green-500/20 backdrop-blur-sm rounded-full px-6 py-2 mb-8 border border-white/10"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.6 }}
                >
                  <Award className="w-5 h-5 text-yellow-400" />
                  <span className="text-sm text-white/90">Trusted by 10,000+ contractors</span>
                </motion.div>

                <motion.h1 
                  className="text-5xl md:text-7xl font-bold text-white mb-6"
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2, duration: 0.8 }}
                >
                  Stop Paying for Leads
                  <span className="block bg-gradient-to-r from-green-400 to-blue-400 bg-clip-text text-transparent">
                    Start Winning Jobs
                  </span>
                </motion.h1>

                <motion.p 
                  className="text-xl md:text-2xl text-white/80 mb-8 max-w-3xl mx-auto"
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4, duration: 0.8 }}
                >
                  Join InstaBids - the only platform where contractors pay nothing until they win. No lead fees, no monthly costs, just results.
                </motion.p>

                {/* Stats */}
                <motion.div 
                  className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12"
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6, duration: 0.8 }}
                >
                  {stats.map((stat, index) => (
                    <motion.div 
                      key={index}
                      className="text-center"
                      whileHover={{ scale: 1.05 }}
                      transition={{ type: "spring", stiffness: 400, damping: 10 }}
                    >
                      <div className="text-3xl md:text-4xl font-bold text-white mb-2">{stat.value}</div>
                      <div className="text-sm text-white/60">{stat.label}</div>
                    </motion.div>
                  ))}
                </motion.div>

                <motion.button
                  onClick={handleStartOnboarding}
                  className="bg-gradient-to-r from-green-600 to-blue-600 text-white py-4 px-8 rounded-xl font-bold text-lg hover:from-green-700 hover:to-blue-700 transition-all duration-300 flex items-center justify-center gap-2 shadow-2xl mx-auto"
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.8, duration: 0.8 }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Get Started - It's Free
                  <ArrowRight className="w-5 h-5" />
                </motion.button>
              </div>
            </section>

            {/* Benefits Section */}
            <section className="py-20 px-4">
              <div className="max-w-6xl mx-auto">
                <div className="text-center mb-16">
                  <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                    Why Top Contractors Choose InstaBids
                  </h2>
                  <p className="text-xl text-white/70">
                    Join thousands of contractors who've revolutionized their business
                  </p>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                  {benefits.map((benefit, index) => (
                    <motion.div
                      key={index}
                      className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 hover:bg-white/10 transition-all duration-300"
                      initial={{ opacity: 0, y: 30 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.8 + index * 0.1, duration: 0.6 }}
                      whileHover={{ y: -5, scale: 1.02 }}
                    >
                      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${benefit.gradient} flex items-center justify-center mb-4`}>
                        <benefit.icon className="w-6 h-6 text-white" />
                      </div>
                      <h3 className="text-lg font-semibold text-white mb-2">{benefit.title}</h3>
                      <p className="text-white/70 text-sm">{benefit.description}</p>
                    </motion.div>
                  ))}
                </div>
              </div>
            </section>

            {/* How It Works */}
            <section className="py-20 px-4">
              <div className="max-w-4xl mx-auto">
                <div className="text-center mb-16">
                  <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                    How It Works
                  </h2>
                  <p className="text-xl text-white/70">
                    Get started in minutes, win your first job this week
                  </p>
                </div>

                <div className="grid md:grid-cols-3 gap-8">
                  {[
                    {
                      step: "1",
                      title: "Quick Setup",
                      description: "Chat with our AI to set up your profile in under 5 minutes. No lengthy forms."
                    },
                    {
                      step: "2", 
                      title: "Browse Projects",
                      description: "See pre-qualified projects in your area. Filter by type, budget, and timeline."
                    },
                    {
                      step: "3",
                      title: "Submit & Win",
                      description: "Submit professional bids. Get paid when you win. No upfront costs ever."
                    }
                  ].map((item, index) => (
                    <motion.div
                      key={index}
                      className="text-center"
                      initial={{ opacity: 0, y: 30 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 1.0 + index * 0.2, duration: 0.6 }}
                    >
                      <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center text-2xl font-bold text-white mb-4 mx-auto">
                        {item.step}
                      </div>
                      <h3 className="text-xl font-semibold text-white mb-2">{item.title}</h3>
                      <p className="text-white/70">{item.description}</p>
                    </motion.div>
                  ))}
                </div>
              </div>
            </section>

            {/* Final CTA */}
            <section className="py-20 px-4">
              <div className="max-w-2xl mx-auto text-center">
                <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 border border-white/20">
                  <h2 className="text-3xl font-bold text-white mb-4">Ready to Stop Paying for Leads?</h2>
                  <p className="text-white/70 mb-8">
                    Join InstaBids today and start winning more profitable projects with zero upfront costs.
                  </p>
                  <button
                    onClick={handleStartOnboarding}
                    className="w-full bg-gradient-to-r from-green-600 to-blue-600 text-white py-4 px-8 rounded-xl font-bold text-lg hover:from-green-700 hover:to-blue-700 transition-all duration-300 flex items-center justify-center gap-2 shadow-lg"
                  >
                    Start Your Free Setup
                    <ArrowRight className="w-5 h-5" />
                  </button>
                  <p className="text-xs text-white/50 mt-4">
                    No credit card required. Setup takes less than 5 minutes.
                  </p>
                </div>
              </div>
            </section>
          </>
        ) : (
          /* Onboarding Chat Section */
          <section className="py-8 px-4">
            <div className="max-w-4xl mx-auto">
              <div className="bg-white/10 backdrop-blur-lg rounded-3xl border border-white/20 overflow-hidden">
                <div className="p-6 border-b border-white/20">
                  <div className="flex items-center justify-between">
                    <h2 className="text-2xl font-bold text-white">Let's Get You Set Up</h2>
                    <button
                      onClick={() => setShowOnboarding(false)}
                      className="text-white/60 hover:text-white transition-colors"
                    >
                      ← Back
                    </button>
                  </div>
                  <p className="text-white/70 mt-2">
                    I'll help you create your contractor profile and find your first project opportunity.
                  </p>
                </div>
                <ContractorOnboardingChat
                  sessionId={sessionId}
                  onComplete={handleOnboardingComplete}
                />
              </div>
            </div>
          </section>
        )}
      </div>
    </div>
  )
}

export default ContractorLandingPage