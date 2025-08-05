"""
Admin Routes - Admin Dashboard and Management API Endpoints
Owner: Agent 2 (Backend Core) - Currently building admin dashboard
"""

from datetime import datetime

from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    Response,
    WebSocket,
    WebSocketDisconnect,
)

import database_simple as database
from admin.auth_service import AdminLoginRequest, admin_auth_service

# Import admin monitoring components
from admin.monitoring_service import AdminMonitoringService
from admin.websocket_manager import AdminWebSocketManager


# Create router
router = APIRouter()

# Initialize admin services
admin_websocket_manager = AdminWebSocketManager()
admin_monitoring_service = AdminMonitoringService()

# Admin WebSocket endpoint for real-time dashboard
@router.websocket("/ws/admin")
async def admin_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for admin dashboard real-time updates"""
    # Don't accept here - let the manager handle it

    client_id = f"admin_{datetime.now().timestamp()}"
    admin_user_id = None

    try:
        # Accept connection first
        await websocket.accept()
        print(f"[ADMIN WS] Connection accepted for {client_id}")

        # Send test message immediately
        try:
            await websocket.send_json({"type": "test", "message": "WebSocket connected successfully"})
            print("[ADMIN WS] Test message sent")
        except Exception as e:
            print(f"[ADMIN WS] Error sending test message: {e}")
            await websocket.close()
            return

        # Wait for authentication message
        print("[ADMIN WS] Waiting for auth message...")
        auth_data = await websocket.receive_json()
        print(f"[ADMIN WS] Received data: {auth_data}")

        if auth_data.get("type") != "auth":
            await websocket.send_json({
                "type": "error",
                "message": "Authentication required"
            })
            await websocket.close()
            return

        # Verify admin session
        session_id = auth_data.get("session_id")
        if not session_id:
            await websocket.send_json({
                "type": "error",
                "message": "Session ID required"
            })
            await websocket.close()
            return

        # Validate session
        print(f"[ADMIN WS] Validating session: {session_id}")
        admin_user = await admin_auth_service.validate_session(session_id)
        if not admin_user:
            print("[ADMIN WS] Session validation failed")
            await websocket.send_json({
                "type": "error",
                "message": "Invalid or expired session"
            })
            await websocket.close()
            return

        print(f"[ADMIN WS] Session validated for user: {admin_user.email}")
        admin_user_id = admin_user.id

        # Register connection with correct parameter order
        connection_success = await admin_websocket_manager.connect(websocket, client_id, admin_user_id)

        # Send authentication success
        await websocket.send_json({
            "type": "auth_success",
            "client_id": client_id,
            "admin_user": {
                "id": admin_user.id,
                "email": admin_user.email,
                "full_name": admin_user.full_name,
                "role": admin_user.role,
                "permissions": admin_user.permissions
            }
        })

        # Send initial dashboard data
        try:
            dashboard_data = await admin_monitoring_service.get_dashboard_overview()
            await websocket.send_json({
                "type": "dashboard_overview",
                "data": dashboard_data,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            print(f"[ADMIN WS] Error getting dashboard data: {e}")
            # Send minimal dashboard data on error
            await websocket.send_json({
                "type": "dashboard_overview",
                "data": {
                    "error": "Failed to load dashboard data",
                    "metrics": {},
                    "agent_statuses": {},
                    "recent_activity": []
                },
                "timestamp": datetime.now().isoformat()
            })

        # Keep connection alive and handle messages
        while True:
            try:
                message = await websocket.receive_json()
                message_type = message.get("type")

                if message_type == "subscribe":
                    # Handle subscription to specific data types
                    subscriptions = message.get("subscriptions", [])
                    # Subscribe to each subscription type
                    for subscription in subscriptions:
                        await admin_websocket_manager.subscribe_client(client_id, subscription)

                elif message_type == "ping":
                    # Handle ping for connection health
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })

                elif message_type == "get_data":
                    # Handle specific data requests
                    data_type = message.get("data_type")

                    if data_type == "agent_status":
                        agent_statuses = await admin_monitoring_service.get_all_agent_statuses()
                        await websocket.send_json({
                            "type": "agent_status_data",
                            "data": agent_statuses,
                            "timestamp": datetime.now().isoformat()
                        })

                    elif data_type == "system_metrics":
                        metrics = await admin_monitoring_service.collect_system_metrics()
                        await websocket.send_json({
                            "type": "system_metrics_data",
                            "data": metrics,
                            "timestamp": datetime.now().isoformat()
                        })

                    elif data_type == "bid_cards":
                        # Get recent bid cards
                        try:
                            bid_cards = await admin_monitoring_service.get_recent_bid_cards(limit=20)
                        except Exception as e:
                            print(f"[ADMIN WS] Bid cards error: {e}")
                            bid_cards = []
                        await websocket.send_json({
                            "type": "bid_cards_data",
                            "data": {"bid_cards": bid_cards},
                            "timestamp": datetime.now().isoformat()
                        })

            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"[ADMIN WS] Error handling message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Error processing message: {e!s}"
                })

    except WebSocketDisconnect:
        print(f"[ADMIN WS] WebSocket disconnected for {client_id}")
    except Exception as e:
        print(f"[ADMIN WS] Connection error: {e}")
        import traceback
        traceback.print_exc()
        # Try to send error to client
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Server error: {e!s}"
            })
        except:
            pass
    finally:
        # Clean up connection
        if client_id:
            print(f"[ADMIN WS] Cleaning up connection for {client_id}")
            await admin_websocket_manager.disconnect(client_id)

# Admin API endpoints
@router.post("/login")
async def admin_login(request: Request, response: Response, login_data: dict):
    """Admin login endpoint"""
    try:
        email = login_data.get("email")
        password = login_data.get("password")
        remember_me = login_data.get("remember_me", False)

        if not email or not password:
            return {"success": False, "error": "Email and password required"}

        # Get client info
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")

        # Create AdminLoginRequest object
        login_request = AdminLoginRequest(
            email=email,
            password=password,
            remember_me=remember_me
        )

        # Authenticate admin
        session = await admin_auth_service.authenticate_admin(login_request, client_ip, user_agent)

        # Set session cookie
        response.set_cookie(
            key="admin_session_id",
            value=session.session_id,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=30 * 24 * 60 * 60 if remember_me else 8 * 60 * 60  # 30 days or 8 hours
        )

        # Convert session to dict for JSON response
        return {
            "success": True,
            "session": {
                "session_id": session.session_id,
                "admin_user_id": session.admin_user_id,
                "email": session.email,
                "created_at": session.created_at.isoformat(),
                "expires_at": session.expires_at.isoformat(),
                "is_active": session.is_active
            },
            "admin_user": {
                "email": session.email,
                "permissions": ["view_dashboard", "monitor_agents", "control_campaigns", "view_database", "manage_system", "export_data", "manage_users"]
            }
        }

    except Exception as e:
        print(f"[ADMIN LOGIN ERROR] {e}")
        return {"success": False, "error": "Login failed"}

@router.post("/logout")
async def admin_logout(response: Response, logout_data: dict):
    """Admin logout endpoint"""
    try:
        session_id = logout_data.get("session_id")
        if not session_id:
            return {"success": False, "error": "Session ID required"}

        success = await admin_auth_service.invalidate_session(session_id)

        # Clear session cookie
        response.delete_cookie(key="admin_session_id")

        return {"success": success}

    except Exception as e:
        print(f"[ADMIN LOGOUT ERROR] {e}")
        return {"success": False, "error": "Logout failed"}

@router.get("/session/validate")
async def validate_admin_session(session_id: str):
    """Validate admin session"""
    try:
        print(f"[ADMIN SESSION VALIDATION] Validating session: {session_id}")
        admin_user = await admin_auth_service.validate_session(session_id)
        if admin_user:
            print(f"[ADMIN SESSION VALIDATION] Session valid for user: {admin_user.email}")
            return {
                "valid": True,
                "session": {
                    "session_id": session_id,
                    "admin_user_id": admin_user.id,
                    "email": admin_user.email
                },
                "admin_user": {
                    "id": admin_user.id,
                    "email": admin_user.email,
                    "full_name": admin_user.full_name,
                    "role": admin_user.role,
                    "permissions": admin_user.permissions
                }
            }
        else:
            print("[ADMIN SESSION VALIDATION] Session invalid or expired")
            return {"valid": False}

    except Exception as e:
        print(f"[ADMIN SESSION VALIDATION ERROR] {e}")
        import traceback
        traceback.print_exc()
        # Write error to file for debugging
        with open("validation_error.log", "a") as f:
            f.write(f"\n[{datetime.now()}] Session validation error for {session_id}: {e}\n")
            f.write(traceback.format_exc())
        return {"valid": False, "error": "Validation failed"}

@router.get("/session")
async def get_current_session(request: Request):
    """Get current admin session from cookies or header"""
    try:
        # Try to get session ID from X-Session-ID header first
        session_id = request.headers.get("X-Session-ID")

        # If not in header, try to get from cookie
        if not session_id:
            session_id = request.cookies.get("admin_session_id")

        # If not in cookie, try Authorization header
        if not session_id:
            auth_header = request.headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                session_id = auth_header.replace("Bearer ", "")

        if not session_id:
            return {"success": False, "error": "No session"}

        # Validate session
        admin_user = await admin_auth_service.validate_session(session_id)

        if admin_user:
            return {
                "success": True,
                "session": {
                    "session_id": session_id,
                    "admin_user_id": admin_user.id,
                    "email": admin_user.email,
                    "created_at": admin_user.created_at.isoformat(),
                    "expires_at": datetime.now().isoformat(),  # Could be improved to get actual expiry
                    "is_active": True
                },
                "admin_user": {
                    "id": admin_user.id,
                    "email": admin_user.email,
                    "full_name": admin_user.full_name,
                    "role": admin_user.role,
                    "permissions": admin_user.permissions,
                    "created_at": admin_user.created_at.isoformat(),
                    "last_login": admin_user.last_login.isoformat() if admin_user.last_login else None,
                    "is_active": admin_user.is_active
                }
            }
        else:
            return {"success": False, "error": "Invalid session"}

    except Exception as e:
        print(f"[ADMIN SESSION ERROR] {e}")
        return {"success": False, "error": "Session validation failed"}

@router.get("/bid-cards")
async def get_admin_bid_cards(request: Request):
    """Get bid cards for admin dashboard"""
    try:
        # Get session ID from Authorization header
        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(401, "Authorization header required")

        session_id = auth_header.replace("Bearer ", "")
        admin_user = await admin_auth_service.validate_session(session_id)
        if not admin_user:
            raise HTTPException(401, "Invalid session")

        # Get recent bid cards from Supabase database
        try:
            # Query real bid cards from Supabase
            response = database.db.client.table("bid_cards").select(
                "id, bid_card_number, project_type, status, contractor_count_needed, "
                "budget_min, budget_max, location_city, location_state, urgency_level, "
                "created_at, updated_at, bid_count, interested_contractors, bid_deadline"
            ).order("created_at", desc=True).execute()

            bid_cards = []
            for card in response.data:
                # Calculate progress percentage
                bid_count = card.get("bid_count", 0)
                contractor_count_needed = card.get("contractor_count_needed", 1)
                progress_percentage = (bid_count / contractor_count_needed * 100) if contractor_count_needed > 0 else 0
                
                # Set intelligent urgency if null based on project type and timeline
                urgency_level = card.get("urgency_level")
                if not urgency_level:
                    project_type = card.get("project_type", "").lower()
                    
                    # Intelligent urgency assignment based on project type
                    if any(keyword in project_type for keyword in ["emergency", "leak", "flood", "urgent", "asap"]):
                        urgency_level = "emergency"
                    elif any(keyword in project_type for keyword in ["roof", "plumbing", "electrical", "hvac"]):
                        urgency_level = "urgent"  # Infrastructure projects are usually urgent
                    elif any(keyword in project_type for keyword in ["kitchen", "bathroom", "remodel"]):
                        urgency_level = "week"  # Major remodels need planning but have deadlines
                    elif any(keyword in project_type for keyword in ["landscape", "paint", "deck", "fence"]):
                        urgency_level = "month"  # Exterior/aesthetic projects more flexible
                    else:
                        urgency_level = "week"  # Default to week (not standard) for active projects
                
                bid_cards.append({
                    "id": card["id"],
                    "bid_card_number": card.get("bid_card_number", "Unknown"),
                    "project_type": card.get("project_type", "Unknown Project"),
                    "status": card.get("status", "unknown"),
                    "bids_received": bid_count,  # Fix: use correct field name
                    "contractor_count_needed": contractor_count_needed,
                    "progress_percentage": round(progress_percentage, 1),  # Fix: calculate percentage
                    "urgency_level": urgency_level,  # Fix: include urgency level
                    "budget_min": card.get("budget_min", 0),
                    "budget_max": card.get("budget_max", 0),
                    "location": f"{card.get('location_city', '')}, {card.get('location_state', '')}".strip(", "),
                    "created_at": card.get("created_at", ""),
                    "updated_at": card.get("updated_at", ""),
                    "last_activity": "Database sync"  # Frontend expects this
                })

            print(f"[ADMIN BID CARDS] Retrieved {len(bid_cards)} real bid cards from database")

        except Exception as e:
            print(f"[ADMIN BID CARDS] Database error: {e}")
            # Return empty array if database fails
            bid_cards = []

        return {
            "success": True,
            "bid_cards": bid_cards,
            "count": len(bid_cards)
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ADMIN BID CARDS ERROR] {e}")
        raise HTTPException(500, "Failed to get bid cards")

@router.post("/restart-agent")
async def restart_agent(restart_data: dict):
    """Restart a specific agent"""
    try:
        session_id = restart_data.get("session_id")
        agent_name = restart_data.get("agent_name")

        if not session_id or not agent_name:
            raise HTTPException(400, "Session ID and agent name required")

        # Validate admin session and permissions
        admin_user = await admin_auth_service.validate_session(session_id)
        if not admin_user:
            raise HTTPException(401, "Invalid session")

        # Check if user has system management permission
        if "manage_system" not in admin_user.permissions:
            raise HTTPException(403, "Insufficient permissions")

        # Restart agent (placeholder - would implement actual restart logic)
        success = await admin_monitoring_service.restart_agent(agent_name)

        if success:
            # Broadcast agent restart to all admin connections
            restart_message = {
                "type": "agent_status",
                "data": {
                    "agent": agent_name,
                    "status": "online",
                    "health_score": 100,
                    "response_time": 0.1,
                    "last_seen": datetime.now().isoformat()
                },
                "timestamp": datetime.now().isoformat()
            }
            await admin_websocket_manager.broadcast_to_all(restart_message)

            return {"success": True, "message": f"Agent {agent_name} restarted successfully"}
        else:
            return {"success": False, "error": f"Failed to restart agent {agent_name}"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ADMIN RESTART AGENT ERROR] {e}")
        raise HTTPException(500, "Failed to restart agent")

@router.get("/dashboard")
async def get_admin_dashboard(request: Request):
    """Get admin dashboard data"""
    try:
        # Try to get session ID from X-Session-ID header first
        session_id = request.headers.get("X-Session-ID")

        # If not in header, try Authorization header
        if not session_id:
            auth_header = request.headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                session_id = auth_header.replace("Bearer ", "")

        # If not in Authorization header, try cookie
        if not session_id:
            session_id = request.cookies.get("admin_session_id")

        if not session_id:
            raise HTTPException(401, "No session provided")

        # Validate admin session
        admin_user = await admin_auth_service.validate_session(session_id)
        if not admin_user:
            raise HTTPException(401, "Invalid session")

        # Get real dashboard data from the monitoring service
        dashboard_data = await admin_monitoring_service.get_dashboard_overview()

        return dashboard_data

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ADMIN DASHBOARD ERROR] {e}")
        raise HTTPException(500, "Failed to get dashboard data")

@router.get("/bid-cards-fixed")
async def get_admin_bid_cards_fixed(request: Request):
    """Get bid cards for admin dashboard - FIXED VERSION with correct field names and calculations"""
    try:
        # Get session ID from Authorization header
        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(401, "Authorization header required")

        session_id = auth_header.replace("Bearer ", "")
        admin_user = await admin_auth_service.validate_session(session_id)
        if not admin_user:
            raise HTTPException(401, "Invalid session")

        # Get recent bid cards from Supabase database
        try:
            # Query real bid cards from Supabase with FIXED logic
            response = database.db.client.table("bid_cards").select(
                "id, bid_card_number, project_type, status, contractor_count_needed, "
                "budget_min, budget_max, location_city, location_state, urgency_level, "
                "created_at, updated_at, bid_count, interested_contractors, bid_deadline"
            ).order("created_at", desc=True).execute()

            bid_cards = []
            for card in response.data:
                # Calculate progress percentage - FIXED CALCULATION
                bid_count = card.get("bid_count", 0)
                contractor_count_needed = card.get("contractor_count_needed", 1)
                progress_percentage = (bid_count / contractor_count_needed * 100) if contractor_count_needed > 0 else 0
                
                # Set intelligent urgency if null based on project type - FIXED URGENCY
                urgency_level = card.get("urgency_level")
                if not urgency_level:
                    project_type = card.get("project_type", "").lower()
                    
                    # Intelligent urgency assignment based on project type
                    if any(keyword in project_type for keyword in ["emergency", "leak", "flood", "urgent", "asap"]):
                        urgency_level = "emergency"
                    elif any(keyword in project_type for keyword in ["roof", "plumbing", "electrical", "hvac"]):
                        urgency_level = "urgent"  # Infrastructure projects are usually urgent
                    elif any(keyword in project_type for keyword in ["kitchen", "bathroom", "remodel"]):
                        urgency_level = "week"  # Major remodels need planning but have deadlines
                    elif any(keyword in project_type for keyword in ["landscape", "paint", "deck", "fence"]):
                        urgency_level = "month"  # Exterior/aesthetic projects more flexible
                    else:
                        urgency_level = "week"  # Default to week (not standard) for active projects
                
                bid_cards.append({
                    "id": card["id"],
                    "bid_card_number": card.get("bid_card_number", "Unknown"),
                    "project_type": card.get("project_type", "Unknown Project"),
                    "status": card.get("status", "unknown"),
                    "bids_received": bid_count,  # FIXED: use correct field name
                    "contractor_count_needed": contractor_count_needed,  # FIXED: include this field
                    "progress_percentage": round(progress_percentage, 1),  # FIXED: calculate percentage
                    "urgency_level": urgency_level,  # FIXED: include urgency level
                    "budget_min": card.get("budget_min", 0),
                    "budget_max": card.get("budget_max", 0),
                    "location": f"{card.get('location_city', '')}, {card.get('location_state', '')}"
                        .strip(", "),
                    "created_at": card.get("created_at", ""),
                    "updated_at": card.get("updated_at", ""),
                    "last_activity": "Database sync"  # Frontend expects this
                })

            print(f"[ADMIN BID CARDS FIXED] Retrieved {len(bid_cards)} real bid cards from database")

        except Exception as e:
            print(f"[ADMIN BID CARDS FIXED] Database error: {e}")
            # Return empty array if database fails
            bid_cards = []

        return {
            "success": True,
            "bid_cards": bid_cards,
            "count": len(bid_cards),
            "message": "FIXED VERSION - Correct field names and calculations"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ADMIN BID CARDS FIXED ERROR] {e}")
        raise HTTPException(500, "Failed to get bid cards")
