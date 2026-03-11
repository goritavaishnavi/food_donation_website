# TODO List - AI Food Detection & Real-time Notifications

## Phase 1: Dependencies
- [x] Update requirements.txt with Flask-SocketIO and dependencies

## Phase 2: Backend (app.py)
- [x] Add Flask-SocketIO to app.py
- [x] Add WebSocket events for real-time notifications
- [x] Add helper function to broadcast notifications

## Phase 3: Frontend - Post Donation (templates/post_donation.html)
- [x] Add camera capture button
- [x] Add TensorFlow.js for food detection
- [x] Add video element for camera preview
- [x] Add canvas for image capture
- [x] Add food detection logic with MobileNet
- [x] Auto-fill food type based on detection
- [x] Show confidence score

## Phase 4: Frontend - Base Template (templates/base.html)
- [x] Add Socket.IO client library
- [x] Add WebSocket connection logic
- [x] Add real-time notification toast UI
- [x] Handle incoming notifications

## Phase 5: Testing
- [ ] Install dependencies: pip install -r requirements.txt
- [ ] Run the app: python app.py
- [ ] Test WebSocket connection
- [ ] Test camera capture
- [ ] Test food detection
- [ ] Test real-time notifications

