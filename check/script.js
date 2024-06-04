let APP_ID = "f237608483cb4366ad5a667053e34e98";
let token = null;
let uid = String(Math.floor(Math.random() * 100000));
let client;
let channel;

let queryString = window.location.search;
let urlParams = new URLSearchParams(queryString);
let roomId = urlParams.get('room');
if (!roomId) {
    window.location = 'lobby.html'
}

let localStream;
let remoteStream;
let peerConnection;
const servers = {
    iceServers: [
        {
            urls: ['stun:stun1.l.google.com:19302', 'stun:stun2.l.google.com:19302']
        }
    ]
}

let constraints = {
    video: {
        width: { min: 640, ideal: 1920, max: 1920 },
        height: { min: 480, ideal: 1080, max: 1080 },
    },
    audio: true
}
let init = async () => {
    client = await AgoraRTM.createInstance(APP_ID);
    await client.login({ uid, token });

    channel = client.createChannel(roomId);
    await channel.join();

    channel.on('MemberJoined', handleUserJoined);
    channel.on('MemberLeft', handleUserLeft);

    client.on('MessageFromPeer', handleMessageFromPeer);

    // Fetch and set local video stream from the specified URL
    const url = 'http://localhost:5000/video_feed';
    console.log("waiting for stream")
    localStream = await createMediaStreamFromURL(url);
    console.log(" stream")

    // localStream =('http://localhost:5000/video_feed');
    document.getElementById("user-1").src = localStream;

    // Update the img tag with frames from the video feed URL for the remote stream
    // updateImage('http://localhost:5000/video_feed', document.getElementById('user-2'));

    createOffer();
}

async function fetchVideoStream(url) {
    console.log("inside fetch func")
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error('Failed to fetch video stream');
    }
    const stream = await response.blob();
    console.log("response")
    console.log(stream)
    return stream;
}

async function createMediaStreamFromURL(url) {
    console.log("inside create funct")
    const stream = await fetchVideoStream(url);
    return new MediaStream([stream]);
}


let handleMessageFromPeer = async (message, MemberId) => {
    message = JSON.parse(message.text)
    console.log('message: ', message);
    if (message.type === "offer") {
        createAnswer(MemberId, message.offer)
    }
    if (message.type === "answer") {
        addAnswer(message.answer)
    }
    if (message.type === "candidate") {
        if (peerConnection) {
            peerConnection.addIceCandidate(message.candidate)
        }
    }
}

let handleUserJoined = async (MemberId) => {
    console.log('A new user joined the channel:', MemberId)
    createOffer(MemberId);
}

let handleUserLeft = async (MemberId) => {
    document.getElementById('user-2').style.display = 'none';
    document.getElementById("user-1").classList.remove('smallFrame');
}

let createPeerConnection=async(MemberId)=>{

    peerConnection=new RTCPeerConnection(servers);

    remoteStream=new MediaStream();
    document.getElementById("user-2").srcObject=remoteStream;
    document.getElementById("user-2").style.display='block';

    document.getElementById("user-1").classList.add('smallFrame');

    if(!localStream){
        localStream = await navigator.mediaDevices.getUserMedia({video:true,audio:false});
    console.log(localStream)
    document.getElementById("user-1").src=localStream;

    }
    console.log(localStream.getTracks());
    localStream.getTracks().forEach((track) => {
        peerConnection.addTrack(track,localStream)
        
    });

    console.log(peerConnection);
    peerConnection.ontrack=(event)=>{
        event.streams[0].getTracks().forEach((track)=>{
            remoteStream.addTrack(track)
        })
    }
    peerConnection.onicecandidate=async (event)=>{
        if(event.candidate){
            console.log("New ICE candidate:",event.candidate)
            client.sendMessageToPeer({'text':JSON.stringify({'type':'candidate','candidate':event.candidate})},MemberId)
        }
    }
}

let createOffer=async (MemberId)=>{
    if (MemberId){
        await createPeerConnection(MemberId);

        let offer=await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);
    
        client.sendMessageToPeer({'text':JSON.stringify({'type':'offer','offer':offer})},MemberId)
    }

    
}

let createAnswer=async (MemberId,offer)=>{
    await createPeerConnection(MemberId);

    await peerConnection.setRemoteDescription(offer)

    let answer=await peerConnection.createAnswer()
    await peerConnection.setLocalDescription(answer);

    client.sendMessageToPeer({'text':JSON.stringify({'type':'answer','answer':answer})},MemberId)
}

let addAnswer=async(answer)=>{
    if(!peerConnection.currentRemoteDescription){
        await peerConnection.setRemoteDescription(answer)
    }
}

let leaveChannel=async ()=>{
    await channel.leave();
    await client.logout();
}

let toggleCamera=async()=> {
    let videoTrack=localStream.getTracks().find(track=>track.kind==='video');
    if(videoTrack.enabled){
        videoTrack.enabled=false;
        document.getElementById('camera-btn').style.backgroundColor= 'rgb(149, 22, 22)';
    }
    else{
        videoTrack.enabled=true;
        document.getElementById('camera-btn').style.backgroundColor= 'rgba(108, 108, 108, 0.793)';
    }
}

let toggleMic=async()=> {
    let audioTrack=localStream.getTracks().find(track=>track.kind==='audio');
    if(audioTrack.enabled){
        audioTrack.enabled=false;
        document.getElementById('mic-btn').style.backgroundColor= 'rgb(149, 22, 22)';
    }
    else{
        audioTrack.enabled=true;
        document.getElementById('mic-btn').style.backgroundColor= 'rgba(108, 108, 108, 0.793)';
    }
}
window.addEventListener('beforeunload',leaveChannel)
document.getElementById('leave-btn').addEventListener('click',leaveChannel)
document.getElementById('camera-btn').addEventListener('click',toggleCamera)
document.getElementById('mic-btn').addEventListener('click',toggleMic)
init()