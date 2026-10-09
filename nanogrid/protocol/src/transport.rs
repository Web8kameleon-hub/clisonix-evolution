use std::net::{TcpListener, TcpStream};
use std::io::{Read, Write};
use serde_cbor;
use crate::TideLevel;

pub struct TcpTransport {
    pub bind_addr: String,
}

impl TcpTransport {
    pub fn start_listener(&self, handler: impl Fn(Vec<u8>) + Send + 'static) {
        let listener = TcpListener::bind(&self.bind_addr).unwrap();

        std::thread::spawn(move || {
            for stream in listener.incoming() {
                if let Ok(mut s) = stream {
                    let mut buf = vec![0u8; 65536];
                    if let Ok(n) = s.read(&mut buf) {
                        handler(buf[..n].to_vec());
                    }
                }
            }
        });
    }

    pub fn send(&self, addr: &str, data: &[u8]) {
        if let Ok(mut stream) = TcpStream::connect(addr) {
            let _ = stream.write_all(data);
        }
    }
}

pub enum GossipFrame {
    Digest(Vec<u8>),
    Delta(Vec<u8>),
    Bulk(Vec<u8>),
}

impl TcpTransport {
    pub fn send_frame(&self, peer: &str, frame: GossipFrame) {
        let bytes = match frame {
            GossipFrame::Digest(d) => d,
            GossipFrame::Delta(d) => d,
            GossipFrame::Bulk(b) => b,
        };

        self.send(peer, &bytes);
    }

    pub fn tide_send(&self, peer: &str, frame: GossipFrame, tide: TideLevel) {
        match tide {
            TideLevel::High => {
                // dërgo menjëherë
                self.send_frame(peer, frame);
            }
            TideLevel::Normal => {
                // dërgo me pak vonesë
                std::thread::sleep(std::time::Duration::from_millis(50));
                self.send_frame(peer, frame);
            }
            TideLevel::Low => {
                // dërgo vetëm Digest/Delta, jo Bulk
                match frame {
                    GossipFrame::Bulk(_) => return,
                    _ => self.send_frame(peer, frame),
                }
            }
        }
    }
}